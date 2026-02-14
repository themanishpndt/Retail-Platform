"""
Computer Vision API Views
REST endpoints for image analysis and shelf intelligence
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
# from django_filters.rest_framework import DjangoFilterBackend
from django.core.files.base import ContentFile
from datetime import datetime
import base64
import numpy as np
from PIL import Image
import io

from .models import (
    ProductDetectionModel, StockLevelDetectionTask,
    ShelfAnalysisResult, ProductRecognitionData, VisionAnalyticMetrics
)
from .serializers import (
    ProductDetectionModelSerializer, StockLevelDetectionTaskSerializer,
    ShelfAnalysisResultSerializer, ProductRecognitionDataSerializer,
    VisionAnalyticMetricsSerializer
)
from .vision_processing import ShelfDetector, ProductRecognizer, ImagePreprocessor


class ProductDetectionModelViewSet(viewsets.ModelViewSet):
    """API endpoint for CV detection models"""
    
    queryset = ProductDetectionModel.objects.all()
    serializer_class = ProductDetectionModelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    # filterset_fields = ['model_type', 'is_active']
    ordering_fields = ['created_at', 'accuracy']
    ordering = ['-accuracy']


class StockLevelDetectionTaskViewSet(viewsets.ModelViewSet):
    """API endpoint for shelf detection tasks"""
    
    queryset = StockLevelDetectionTask.objects.select_related('model', 'store')
    serializer_class = StockLevelDetectionTaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    # filterset_fields = ['model', 'store', 'status']
    ordering_fields = ['created_at', 'processed_at']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Process shelf image for detection"""
        task = self.get_object()
        
        if task.status != 'pending':
            return Response(
                {'error': 'Task already processed'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            task.status = 'processing'
            task.save()
            
            # Load image
            from django.core.files.storage import default_storage
            image_path = task.image.path if hasattr(task.image, 'path') else None
            
            if not image_path:
                raise ValueError("Image file not found")
                
            # Initialize detector
            detector = ShelfDetector(model_type=task.model.model_type.lower())
            detector.load_model(task.model.model_path if task.model.model_path else None)
            
            # Preprocess image
            image = detector.preprocess_image(image_path)
            
            # Detect products
            detections = detector.detect_products(image, confidence_threshold=0.5)
            
            # Detect empty shelves
            empty_sections = detector.detect_empty_shelves(image)
            
            # Save results
            task.detected_products = len(detections)
            task.empty_shelf_count = len(empty_sections)
            task.confidence_score = np.mean([d['confidence'] for d in detections]) if detections else 0.0
            task.detection_results = {
                'products': detections,
                'empty_sections': empty_sections
            }
            task.status = 'completed'
            task.processed_at = datetime.now()
            task.save()
            
            # Create shelf analysis result
            analysis = ShelfAnalysisResult.objects.create(
                detection_task=task,
                store=task.store,
                total_products_detected=len(detections),
                empty_shelf_count=len(empty_sections),
                out_of_stock_count=len(empty_sections),
                shelf_fullness_percentage=max(0, 100 - (len(empty_sections) * 10)),
                quality_score=task.confidence_score * 100
            )
            
            serializer = self.get_serializer(task)
            return Response(serializer.data)
            
        except Exception as e:
            task.status = 'failed'
            task.error_message = str(e)
            task.save()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    @action(detail=False, methods=['post'])
    def analyze_shelf(self, request):
        """Analyze uploaded shelf image"""
        image_data = request.data.get('image')
        store_id = request.data.get('store_id')
        model_id = request.data.get('model_id')
        
        if not image_data:
            return Response({'error': 'image required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Decode base64 image
            if isinstance(image_data, str) and image_data.startswith('data:image'):
                format, imgstr = image_data.split(';base64,')
                image_data = base64.b64decode(imgstr)
            elif isinstance(image_data, str):
                image_data = base64.b64decode(image_data)
                
            # Convert to PIL Image
            image = Image.open(io.BytesIO(image_data))
            image_array = np.array(image)
            
            # Get or create default model
            if model_id:
                model = ProductDetectionModel.objects.get(id=model_id)
            else:
                model = ProductDetectionModel.objects.filter(is_active=True).first()
                
            if not model:
                return Response({'error': 'No active detection model found'}, status=status.HTTP_404_NOT_FOUND)
                
            # Create detection task
            from inventory.models import Store
            store = Store.objects.get(id=store_id) if store_id else None
            
            task = StockLevelDetectionTask.objects.create(
                model=model,
                store=store,
                status='processing'
            )
            
            # Save image
            image_file = ContentFile(image_data, name=f'shelf_{task.id}.jpg')
            task.image = image_file
            task.save()
            
            # Process immediately
            detector = ShelfDetector(model_type=model.model_type.lower())
            
            # Detect products and empty shelves
            detections = detector.detect_products(image_array, confidence_threshold=0.5)
            empty_sections = detector.detect_empty_shelves(image_array)
            
            task.detected_products = len(detections)
            task.empty_shelf_count = len(empty_sections)
            task.confidence_score = np.mean([d['confidence'] for d in detections]) if detections else 0.0
            task.detection_results = {
                'products': detections,
                'empty_sections': empty_sections
            }
            task.status = 'completed'
            task.processed_at = datetime.now()
            task.save()
            
            return Response({
                'task_id': task.id,
                'detections': len(detections),
                'empty_shelves': len(empty_sections),
                'confidence': task.confidence_score,
                'products': detections[:10],  # Return first 10
                'empty_sections': empty_sections
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ShelfAnalysisResultViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for shelf analysis results"""
    
    queryset = ShelfAnalysisResult.objects.select_related('detection_task', 'store')
    serializer_class = ShelfAnalysisResultSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    # filterset_fields = ['store', 'analysis_date']
    ordering_fields = ['analysis_date', 'quality_score']
    ordering = ['-analysis_date']
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest shelf analysis"""
        store_id = request.query_params.get('store_id')
        
        queryset = self.get_queryset()
        if store_id:
            queryset = queryset.filter(store_id=store_id)
            
        result = queryset.first()
        
        if result:
            serializer = self.get_serializer(result)
            return Response(serializer.data)
        return Response({'message': 'No results found'}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get shelf analysis summary"""
        from django.db.models import Avg, Sum, Count
        
        summary = self.get_queryset().aggregate(
            total_analyses=Count('id'),
            avg_fullness=Avg('shelf_fullness_percentage'),
            total_empty_shelves=Sum('empty_shelf_count'),
            avg_quality=Avg('quality_score')
        )
        
        return Response(summary)


class ProductRecognitionViewSet(viewsets.ViewSet):
    """Product recognition endpoint"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def recognize(self, request):
        """Recognize product from image"""
        image_data = request.data.get('image')
        
        if not image_data:
            return Response({'error': 'image required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Decode image
            if isinstance(image_data, str) and image_data.startswith('data:image'):
                format, imgstr = image_data.split(';base64,')
                image_data = base64.b64decode(imgstr)
            elif isinstance(image_data, str):
                image_data = base64.b64decode(image_data)
                
            image = Image.open(io.BytesIO(image_data))
            image_array = np.array(image)
            
            # Initialize recognizer
            recognizer = ProductRecognizer()
            
            # Load training data (in production, this would be cached)
            training_data = ProductRecognitionData.objects.select_related('product').all()
            
            training_dict = {}
            for data in training_data:
                if data.product_id not in training_dict:
                    training_dict[data.product_id] = []
                    
                # Load training image
                if data.training_image:
                    try:
                        train_img = Image.open(data.training_image)
                        training_dict[data.product_id].append(np.array(train_img))
                    except:
                        pass
                        
            if training_dict:
                recognizer.train(training_dict)
                
                # Recognize
                product_id = recognizer.recognize(image_array)
                
                if product_id:
                    from products.models import Product
                    product = Product.objects.get(id=product_id)
                    
                    from products.serializers import ProductSerializer
                    return Response({
                        'recognized': True,
                        'product': ProductSerializer(product).data
                    })
                    
            return Response({
                'recognized': False,
                'message': 'Product not recognized'
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
