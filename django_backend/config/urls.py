"""URL configuration for product_importer project."""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from importer.views import (
    ProductViewSet, ImportJobViewSet, WebhookViewSet,
    UploadCSVView, ImportProgressView, TestWebhookView
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'import-jobs', ImportJobViewSet, basename='import-job')
router.register(r'webhooks', WebhookViewSet, basename='webhook')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Web UI Routes
    path('', include('importer.urls')),
    
    # REST API Routes
    path('api/', include(router.urls)),
    path('api/import/upload/', UploadCSVView.as_view(), name='upload-csv'),
    path('api/import/progress/<str:job_id>/', ImportProgressView.as_view(), name='import-progress'),
    path('api/webhooks/<str:pk>/test/', TestWebhookView.as_view(), name='test-webhook'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api-auth/', include('rest_framework.urls')),
]
