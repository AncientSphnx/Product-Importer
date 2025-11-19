"""Django REST Framework views and Web UI views."""
import uuid
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.http import JsonResponse
from .models import Product, ImportJob, Webhook, WebhookLog
from .serializers import ProductSerializer, ImportJobSerializer, WebhookSerializer, WebhookLogSerializer
from .forms import ProductForm, WebhookForm, CSVUploadForm
from .tasks import import_csv_task, trigger_webhook

logger = logging.getLogger(__name__)

# ============================================================================
# WEB UI VIEWS (Django Templates)
# ============================================================================

class DashboardView(TemplateView):
    """Dashboard view."""
    template_name = 'importer/dashboard.html'

    def get_context_data(self, **kwargs):
        """Get context data."""
        context = super().get_context_data(**kwargs)
        context['total_products'] = Product.objects.count()
        context['active_products'] = Product.objects.filter(active=True).count()
        context['inactive_products'] = Product.objects.filter(active=False).count()
        context['total_webhooks'] = Webhook.objects.count()
        context['recent_imports'] = ImportJob.objects.all()[:5]
        return context


class ProductListView(ListView):
    """Product list view."""
    model = Product
    template_name = 'importer/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        """Filter products based on query parameters."""
        queryset = Product.objects.all()

        sku = self.request.GET.get('sku')
        if sku:
            queryset = queryset.filter(sku__icontains=sku.upper())

        name = self.request.GET.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)

        active = self.request.GET.get('active')
        if active:
            queryset = queryset.filter(active=active.lower() == 'true')

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        """Get context data."""
        context = super().get_context_data(**kwargs)
        context['sku_filter'] = self.request.GET.get('sku', '')
        context['name_filter'] = self.request.GET.get('name', '')
        context['active_filter'] = self.request.GET.get('active', '')
        return context


class ProductCreateView(SuccessMessageMixin, CreateView):
    """Create product view."""
    model = Product
    form_class = ProductForm
    template_name = 'importer/product_form.html'
    success_url = reverse_lazy('importer:product_list')
    success_message = 'Product created successfully'

    def form_valid(self, form):
        """Handle valid form."""
        response = super().form_valid(form)
        trigger_webhook.delay('product_created', {
            'product_id': str(self.object.id),
            'sku': self.object.sku
        })
        return response


class ProductUpdateView(SuccessMessageMixin, UpdateView):
    """Update product view."""
    model = Product
    form_class = ProductForm
    template_name = 'importer/product_form.html'
    success_url = reverse_lazy('importer:product_list')
    success_message = 'Product updated successfully'

    def form_valid(self, form):
        """Handle valid form."""
        response = super().form_valid(form)
        trigger_webhook.delay('product_updated', {
            'product_id': str(self.object.id),
            'sku': self.object.sku
        })
        return response


class ProductDeleteView(SuccessMessageMixin, DeleteView):
    """Delete product view."""
    model = Product
    template_name = 'importer/product_confirm_delete.html'
    success_url = reverse_lazy('importer:product_list')
    success_message = 'Product deleted successfully'

    def delete(self, request, *args, **kwargs):
        """Handle delete."""
        self.object = self.get_object()
        product_id = str(self.object.id)
        sku = self.object.sku
        response = super().delete(request, *args, **kwargs)
        trigger_webhook.delay('product_deleted', {
            'product_id': product_id,
            'sku': sku
        })
        return response


class ImportView(TemplateView):
    """Import CSV view."""
    template_name = 'importer/import.html'

    def get_context_data(self, **kwargs):
        """Get context data."""
        context = super().get_context_data(**kwargs)
        context['form'] = CSVUploadForm()
        context['recent_imports'] = ImportJob.objects.all()[:10]
        return context

    def post(self, request, *args, **kwargs):
        """Handle file upload."""
        # Check if file is in request
        if 'file' not in request.FILES:
            logger.error("No file in request.FILES")
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        file = request.FILES['file']
        
        # Validate file
        if not file.name.endswith('.csv'):
            logger.error(f"Invalid file type: {file.name}")
            return JsonResponse({'error': 'File must be CSV'}, status=400)

        if file.size > 500 * 1024 * 1024:
            logger.error(f"File too large: {file.size} bytes")
            return JsonResponse({'error': 'File too large (max 500MB)'}, status=400)

        try:
            job_id = str(uuid.uuid4())
            job = ImportJob.objects.create(
                id=job_id,
                filename=file.name,
                status='pending'
            )

            content = file.read()
            task = import_csv_task.delay(content, file.name, job_id)

            logger.info(f"Import job created: {job_id}")
            return JsonResponse({
                'job_id': job_id,
                'task_id': task.id,
                'status': 'pending',
                'message': 'Import started'
            })

        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)


class WebhookListView(ListView):
    """Webhook list view."""
    model = Webhook
    template_name = 'importer/webhook_list.html'
    context_object_name = 'webhooks'

    def get_context_data(self, **kwargs):
        """Get context data."""
        context = super().get_context_data(**kwargs)
        for webhook in context['webhooks']:
            webhook.recent_logs = WebhookLog.objects.filter(
                webhook=webhook
            ).order_by('-created_at')[:5]
        return context


class WebhookCreateView(SuccessMessageMixin, CreateView):
    """Create webhook view."""
    model = Webhook
    form_class = WebhookForm
    template_name = 'importer/webhook_form.html'
    success_url = reverse_lazy('importer:webhook_list')
    success_message = 'Webhook created successfully'


class WebhookUpdateView(SuccessMessageMixin, UpdateView):
    """Update webhook view."""
    model = Webhook
    form_class = WebhookForm
    template_name = 'importer/webhook_form.html'
    success_url = reverse_lazy('importer:webhook_list')
    success_message = 'Webhook updated successfully'


class WebhookDeleteView(SuccessMessageMixin, DeleteView):
    """Delete webhook view."""
    model = Webhook
    template_name = 'importer/webhook_confirm_delete.html'
    success_url = reverse_lazy('importer:webhook_list')
    success_message = 'Webhook deleted successfully'

# ============================================================================
# REST API VIEWS (JSON)
# ============================================================================


class ProductViewSet(viewsets.ModelViewSet):
    """Product viewset with CRUD operations."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        """Filter products based on query parameters."""
        queryset = Product.objects.all()

        # Filter by SKU
        sku = self.request.query_params.get('sku')
        if sku:
            queryset = queryset.filter(sku__icontains=sku.upper())

        # Filter by name
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)

        # Filter by active status
        active = self.request.query_params.get('active')
        if active is not None:
            queryset = queryset.filter(active=active.lower() == 'true')

        return queryset.order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """Create a new product."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check if SKU already exists (case-insensitive)
        sku = serializer.validated_data.get('sku', '').upper()
        if Product.objects.filter(sku__iexact=sku).exists():
            return Response(
                {'detail': 'SKU already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_create(serializer)

        # Trigger webhook
        trigger_webhook.delay('product_created', {
            'product_id': str(serializer.instance.id),
            'sku': serializer.instance.sku
        })

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Update a product."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Trigger webhook
        trigger_webhook.delay('product_updated', {
            'product_id': str(instance.id),
            'sku': instance.sku
        })

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Delete a product."""
        instance = self.get_object()
        sku = instance.sku
        product_id = str(instance.id)
        self.perform_destroy(instance)

        # Trigger webhook
        trigger_webhook.delay('product_deleted', {
            'product_id': product_id,
            'sku': sku
        })

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        """Delete all products."""
        count = Product.objects.count()
        Product.objects.all().delete()
        return Response({'message': f'Deleted {count} products'})


class ImportJobViewSet(viewsets.ReadOnlyModelViewSet):
    """Import job viewset (read-only)."""
    queryset = ImportJob.objects.all()
    serializer_class = ImportJobSerializer


class WebhookViewSet(viewsets.ModelViewSet):
    """Webhook viewset with CRUD operations."""
    queryset = Webhook.objects.all()
    serializer_class = WebhookSerializer

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test a webhook."""
        webhook = self.get_object()
        trigger_webhook.delay('test', {'test': True})
        return Response({'message': 'Webhook test triggered'})

    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get webhook delivery logs."""
        webhook = self.get_object()
        limit = request.query_params.get('limit', 50)
        logs = WebhookLog.objects.filter(webhook=webhook).order_by('-created_at')[:int(limit)]
        serializer = WebhookLogSerializer(logs, many=True)
        return Response(serializer.data)


class UploadCSVView(APIView):
    """CSV upload view."""
    parser_classes = (MultiPartParser,)

    def post(self, request):
        """Handle CSV file upload."""
        file = request.FILES.get('file')

        if not file:
            return Response(
                {'detail': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not file.name.endswith('.csv'):
            return Response(
                {'detail': 'File must be CSV'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if file.size > 500 * 1024 * 1024:  # 500 MB
            return Response(
                {'detail': 'File too large'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create import job
            job_id = str(uuid.uuid4())
            job = ImportJob.objects.create(
                id=job_id,
                filename=file.name,
                status='pending'
            )

            # Read file content
            content = file.read()

            # Start async import task
            task = import_csv_task.delay(content, file.name, job_id)

            return Response({
                'job_id': job_id,
                'task_id': task.id,
                'status': 'pending',
                'message': 'Import started'
            }, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ImportProgressView(APIView):
    """Get import job progress."""

    def get(self, request, job_id):
        """Get import job status."""
        try:
            job = ImportJob.objects.get(id=job_id)
            serializer = ImportJobSerializer(job)
            return Response(serializer.data)
        except ImportJob.DoesNotExist:
            return Response(
                {'detail': 'Import job not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class TestWebhookView(APIView):
    """Test webhook view."""

    def post(self, request, pk):
        """Test a webhook."""
        try:
            webhook = Webhook.objects.get(id=pk)
            trigger_webhook.delay('test', {'test': True})
            return Response({'message': 'Webhook test triggered'})
        except Webhook.DoesNotExist:
            return Response(
                {'detail': 'Webhook not found'},
                status=status.HTTP_404_NOT_FOUND
            )
