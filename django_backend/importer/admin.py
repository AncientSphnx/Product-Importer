"""Django admin configuration."""
from django.contrib import admin
from .models import Product, ImportJob, Webhook, WebhookLog


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Product admin."""
    list_display = ['sku', 'name', 'price', 'quantity', 'active', 'created_at']
    list_filter = ['active', 'created_at']
    search_fields = ['sku', 'name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Info', {'fields': ('id', 'sku', 'name', 'description')}),
        ('Inventory', {'fields': ('price', 'quantity')}),
        ('Status', {'fields': ('active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
    """Import job admin."""
    list_display = ['filename', 'status', 'total_records', 'processed_records', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['filename']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Job Info', {'fields': ('id', 'filename', 'status')}),
        ('Progress', {'fields': ('total_records', 'processed_records', 'created_records', 'updated_records')}),
        ('Error', {'fields': ('error_message',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    """Webhook admin."""
    list_display = ['url', 'event_type', 'active', 'created_at']
    list_filter = ['event_type', 'active', 'created_at']
    search_fields = ['url']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Webhook Info', {'fields': ('id', 'url', 'event_type')}),
        ('Status', {'fields': ('active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    """Webhook log admin."""
    list_display = ['webhook', 'event_type', 'status_code', 'response_time_ms', 'created_at']
    list_filter = ['event_type', 'status_code', 'created_at']
    search_fields = ['webhook__url']
    readonly_fields = ['id', 'created_at']
    fieldsets = (
        ('Log Info', {'fields': ('id', 'webhook', 'event_type')}),
        ('Response', {'fields': ('status_code', 'response_time_ms')}),
        ('Error', {'fields': ('error_message',)}),
        ('Timestamp', {'fields': ('created_at',)}),
    )
