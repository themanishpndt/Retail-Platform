from rest_framework import serializers
from .models import (
    ForecastModel, ForecastingTrainingJob,
    DemandForecastingResult, ForecastingMetrics
)


class ForecastModelSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    
    class Meta:
        model = ForecastModel
        fields = [
            'id', 'product', 'product_sku', 'product_name', 'store', 'store_name',
            'model_type', 'algorithm', 'is_active', 'last_trained', 'created_at', 'updated_at'
        ]


class ForecastingTrainingJobSerializer(serializers.ModelSerializer):
    model_id = serializers.IntegerField(source='forecast_model.id', read_only=True)
    
    class Meta:
        model = ForecastingTrainingJob
        fields = [
            'id', 'forecast_model', 'model_id', 'status', 'algorithm', 'training_data_size',
            'test_data_size', 'parameters', 'mae', 'rmse', 'mape', 'r_squared',
            'training_duration_seconds', 'error_message', 'started_at', 'completed_at',
            'created_at', 'updated_at'
        ]


class DemandForecastingResultSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    model_algorithm = serializers.CharField(source='forecast_model.algorithm', read_only=True)
    
    class Meta:
        model = DemandForecastingResult
        fields = [
            'id', 'forecast_model', 'model_algorithm', 'product', 'product_sku', 'product_name',
            'store', 'store_name', 'forecast_date', 'predicted_quantity',
            'confidence_lower', 'confidence_upper', 'actual_quantity', 'error',
            'created_at', 'updated_at'
        ]


class ForecastingMetricsSerializer(serializers.ModelSerializer):
    model_id = serializers.IntegerField(source='forecast_model.id', read_only=True)
    
    class Meta:
        model = ForecastingMetrics
        fields = [
            'id', 'forecast_model', 'model_id', 'period_start', 'period_end',
            'total_predictions', 'average_error', 'mae', 'rmse', 'mape',
            'accuracy_score', 'created_at', 'updated_at'
        ]
