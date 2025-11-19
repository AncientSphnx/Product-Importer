"""Django REST Framework serializers."""
from rest_framework import serializers
from .models import Product, ImportJob, Webhook, WebhookLog


class ProductSerializer(serializers.ModelSerializer):
    """Product serializer."""
    class Meta:
        model = Product
        fields = ['id', 'sku', 'name', 'description', 'price', 'quantity', 'active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ImportJobSerializer(serializers.ModelSerializer):
    """Import job serializer."""
    # Alias fields for frontend compatibility
    total = serializers.IntegerField(source='total_records', read_only=True)
    processed = serializers.IntegerField(source='processed_records', read_only=True)
    
    class Meta:
        model = ImportJob
        fields = ['id', 'filename', 'status', 'total_records', 'processed_records', 
                  'created_records', 'updated_records', 'error_message', 'created_at', 'updated_at',
                  'total', 'processed']
        read_only_fields = ['id', 'created_at', 'updated_at']


class WebhookLogSerializer(serializers.ModelSerializer):
    """Webhook log serializer."""
    class Meta:
        model = WebhookLog
        fields = ['id', 'webhook', 'event_type', 'status_code', 'response_time_ms', 'error_message', 'created_at']
        read_only_fields = ['id', 'created_at']


class WebhookSerializer(serializers.ModelSerializer):
    """Webhook serializer."""
    logs = WebhookLogSerializer(many=True, read_only=True, source='logs')

    class Meta:
        model = Webhook
        fields = ['id', 'url', 'event_type', 'active', 'created_at', 'updated_at', 'logs']
        read_only_fields = ['id', 'created_at', 'updated_at']
