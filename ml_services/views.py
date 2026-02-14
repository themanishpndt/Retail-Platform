"""
ML Services API Views
REST endpoints for machine learning forecasting
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
# from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Avg
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from .models import (
    ForecastModel, ForecastingTrainingJob,
    DemandForecastingResult, ForecastingMetrics
)
from .serializers import (
    ForecastModelSerializer, ForecastingTrainingJobSerializer,
    DemandForecastingResultSerializer, ForecastingMetricsSerializer
)
from .forecasting import DemandForecaster, StockoutPredictor, ProductRecommender


class ForecastModelViewSet(viewsets.ModelViewSet):
    """API endpoint for forecast models"""
    
    queryset = ForecastModel.objects.all()
    serializer_class = ForecastModelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    # filterset_fields = ['model_type', 'is_active']
    ordering_fields = ['created_at', 'accuracy']
    ordering = ['-accuracy']
    
    @action(detail=True, methods=['post'])
    def train(self, request, pk=None):
        """Trigger model training"""
        model = self.get_object()
        product_id = request.data.get('product_id')
        store_id = request.data.get('store_id')
        
        if not product_id:
            return Response({'error': 'product_id required'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Create training job
        job = ForecastingTrainingJob.objects.create(
            model=model,
            status='running',
            parameters={'product_id': product_id, 'store_id': store_id}
        )
        
        try:
            # Get historical sales data
            from orders.models import OrderLine
            sales_data = OrderLine.objects.filter(
                product_id=product_id,
                order__status='completed'
            )
            
            if store_id:
                sales_data = sales_data.filter(order__store_id=store_id)
                
            # Convert to DataFrame
            df = pd.DataFrame(list(sales_data.values('order__order_date', 'quantity')))
            df.columns = ['date', 'quantity']
            df['date'] = pd.to_datetime(df['date'])
            
            # Aggregate by date
            df = df.groupby('date')['quantity'].sum().reset_index()
            
            if len(df) < 30:
                job.status = 'failed'
                job.error_message = 'Insufficient data (minimum 30 days required)'
                job.save()
                return Response({'error': 'Insufficient data'}, status=status.HTTP_400_BAD_REQUEST)
                
            # Train model
            forecaster = DemandForecaster(method=model.model_type.lower())
            
            if model.model_type == 'ARIMA':
                forecaster.train_arima(df['quantity'])
            elif model.model_type == 'LSTM':
                forecaster.train_lstm(df['quantity'].values)
            elif model.model_type == 'Prophet':
                forecaster.train_prophet(df)
                
            # Generate test predictions
            test_size = min(7, len(df) // 4)
            train_data = df[:-test_size]
            test_data = df[-test_size:]
            
            predictions = forecaster.predict(steps=test_size)
            metrics = forecaster.calculate_metrics(test_data['quantity'].values, predictions)
            
            # Save metrics
            ForecastingMetrics.objects.create(
                model=model,
                mae=metrics['mae'],
                rmse=metrics['rmse'],
                mape=metrics['mape'],
                r_squared=metrics['r2']
            )
            
            job.status = 'completed'
            job.metrics = metrics
            job.save()
            
            model.accuracy = max(0, min(100, 100 - metrics['mape']))
            model.last_trained = datetime.now()
            model.save()
            
            return Response({
                'message': 'Training completed',
                'metrics': metrics,
                'job_id': job.id
            })
            
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            job.save()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    @action(detail=True, methods=['post'])
    def predict(self, request, pk=None):
        """Generate forecast predictions"""
        model = self.get_object()
        product_id = request.data.get('product_id')
        store_id = request.data.get('store_id')
        days = int(request.data.get('days', 30))
        
        if not product_id:
            return Response({'error': 'product_id required'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Get historical data
        from orders.models import OrderLine
        sales_data = OrderLine.objects.filter(
            product_id=product_id,
            order__status='completed'
        )
        
        if store_id:
            sales_data = sales_data.filter(order__store_id=store_id)
            
        df = pd.DataFrame(list(sales_data.values('order__order_date', 'quantity')))
        df.columns = ['date', 'quantity']
        df['date'] = pd.to_datetime(df['date'])
        df = df.groupby('date')['quantity'].sum().reset_index()
        
        # Generate forecast
        forecaster = DemandForecaster(method=model.model_type.lower())
        
        if model.model_type == 'ARIMA':
            forecaster.train_arima(df['quantity'])
        elif model.model_type == 'LSTM':
            forecaster.history = df['quantity'].values
            forecaster.train_lstm(df['quantity'].values)
        elif model.model_type == 'Prophet':
            forecaster.train_prophet(df)
            
        predictions = forecaster.predict(steps=days)
        
        # Save results
        from products.models import Product
        from inventory.models import Store
        
        product = Product.objects.get(id=product_id)
        store = Store.objects.get(id=store_id) if store_id else None
        
        results = []
        start_date = datetime.now().date() + timedelta(days=1)
        
        for i, pred in enumerate(predictions):
            result = DemandForecastingResult.objects.create(
                model=model,
                product=product,
                store=store,
                forecast_date=start_date + timedelta(days=i),
                predicted_quantity=max(0, float(pred)),
                confidence_score=model.accuracy / 100.0
            )
            results.append(result)
            
        serializer = DemandForecastingResultSerializer(results, many=True)
        return Response(serializer.data)


class ForecastingResultViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for forecast results"""
    
    queryset = DemandForecastingResult.objects.select_related('model', 'product', 'store')
    serializer_class = DemandForecastingResultSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    # filterset_fields = ['model', 'product', 'store']
    ordering_fields = ['forecast_date', 'predicted_quantity']
    ordering = ['forecast_date']
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming forecasts"""
        days = int(request.query_params.get('days', 7))
        end_date = datetime.now().date() + timedelta(days=days)
        
        results = self.get_queryset().filter(
            forecast_date__gte=datetime.now().date(),
            forecast_date__lte=end_date
        )
        
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)


class RecommendationViewSet(viewsets.ViewSet):
    """Product recommendation endpoint"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def products(self, request):
        """Get product recommendations"""
        product_id = request.data.get('product_id')
        n_recommendations = int(request.data.get('n', 5))
        
        if not product_id:
            return Response({'error': 'product_id required'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Build recommender (in production, this would be cached)
        from orders.models import OrderLine
        
        sales_data = OrderLine.objects.filter(
            order__status='completed'
        ).values('product_id', 'order__customer_id', 'quantity')
        
        df = pd.DataFrame(list(sales_data))
        
        if len(df) < 10:
            return Response({'recommendations': []})
            
        recommender = ProductRecommender()
        features = recommender.build_features(df)
        recommender.fit(features)
        
        try:
            recommended_ids = recommender.recommend_products(int(product_id), n_recommendations)
            
            from products.models import Product
            products = Product.objects.filter(id__in=recommended_ids)
            
            from products.serializers import ProductSerializer
            return Response(ProductSerializer(products, many=True).data)
            
        except:
            return Response({'recommendations': []})
