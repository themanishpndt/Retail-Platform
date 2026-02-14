from rest_framework import serializers
from .models import (
    ProductDetectionModel, StockLevelDetectionTask,
    ShelfAnalysisResult, ProductRecognitionData, VisionAnalyticMetrics
)


class ProductDetectionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDetectionModel
        fields = [
            'id', 'name', 'model_type', 'model_version', 'framework',
            'model_file', 'config_file', 'classes', 'confidence_threshold',
            'iou_threshold', 'is_active', 'accuracy', 'precision_score',
            'recall', 'f1_score', 'training_date', 'created_at', 'updated_at'
        ]


class StockLevelDetectionTaskSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    model_name = serializers.CharField(source='detection_model.name', read_only=True)
    
    class Meta:
        model = StockLevelDetectionTask
        fields = [
            'id', 'store', 'store_name', 'detection_model', 'model_name',
            'image', 'status', 'total_products_detected', 'empty_shelves_detected',
            'shelf_fullness_percentage', 'processing_time_seconds', 'error_message',
            'created_at', 'updated_at', 'completed_at'
        ]


class ShelfAnalysisResultSerializer(serializers.ModelSerializer):
    task_id = serializers.IntegerField(source='detection_task.id', read_only=True)
    
    class Meta:
        model = ShelfAnalysisResult
        fields = [
            'id', 'detection_task', 'task_id', 'shelf_section', 'total_slots',
            'filled_slots', 'empty_slots', 'fullness_percentage', 'detected_products',
            'misplaced_products', 'planogram_compliance_score', 'requires_attention',
            'created_at', 'updated_at'
        ]


class ProductRecognitionDataSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = ProductRecognitionData
        fields = [
            'id', 'product', 'product_sku', 'product_name', 'image',
            'features', 'embedding', 'is_validated', 'validated_by',
            'created_at', 'updated_at'
        ]


class VisionAnalyticMetricsSerializer(serializers.ModelSerializer):
    model_name = serializers.CharField(source='detection_model.name', read_only=True)
    
    class Meta:
        model = VisionAnalyticMetrics
        fields = [
            'id', 'detection_model', 'model_name', 'period_start', 'period_end',
            'total_detections', 'average_confidence', 'false_positives',
            'false_negatives', 'precision_score', 'recall', 'f1_score',
            'average_processing_time', 'created_at', 'updated_at'
        ]
