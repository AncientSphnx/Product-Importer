"""URL configuration for importer app - Web UI routes only."""
from django.urls import path
from . import views

app_name = 'importer'

urlpatterns = [
    # Web UI Routes
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<uuid:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('products/<uuid:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('import/', views.ImportView.as_view(), name='import'),
    path('webhooks/', views.WebhookListView.as_view(), name='webhook_list'),
    path('webhooks/create/', views.WebhookCreateView.as_view(), name='webhook_create'),
    path('webhooks/<uuid:pk>/edit/', views.WebhookUpdateView.as_view(), name='webhook_edit'),
    path('webhooks/<uuid:pk>/delete/', views.WebhookDeleteView.as_view(), name='webhook_delete'),
]
