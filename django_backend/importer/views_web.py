"""Web UI views for Django templates."""
import uuid
import logging
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from .models import Product, ImportJob, Webhook, WebhookLog
from .forms import ProductForm, WebhookForm, CSVUploadForm
from .tasks import import_csv_task, trigger_webhook

logger = logging.getLogger(__name__)


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

        # Filter by SKU
        sku = self.request.GET.get('sku')
        if sku:
            queryset = queryset.filter(sku__icontains=sku.upper())

        # Filter by name
        name = self.request.GET.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)

        # Filter by active status
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
        
        # Trigger webhook
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
        
        # Trigger webhook
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
        
        # Trigger webhook
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
        form = CSVUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            file = form.cleaned_data['file']
            
            if not file.name.endswith('.csv'):
                return JsonResponse({
                    'error': 'File must be CSV'
                }, status=400)

            if file.size > 500 * 1024 * 1024:  # 500 MB
                return JsonResponse({
                    'error': 'File too large'
                }, status=400)

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

                return JsonResponse({
                    'job_id': job_id,
                    'task_id': task.id,
                    'status': 'pending',
                    'message': 'Import started'
                })

            except Exception as e:
                logger.error(f"Error uploading file: {str(e)}")
                return JsonResponse({
                    'error': str(e)
                }, status=400)
        
        return JsonResponse({
            'error': 'Invalid form'
        }, status=400)


class WebhookListView(ListView):
    """Webhook list view."""
    model = Webhook
    template_name = 'importer/webhook_list.html'
    context_object_name = 'webhooks'

    def get_context_data(self, **kwargs):
        """Get context data."""
        context = super().get_context_data(**kwargs)
        
        # Add logs for each webhook
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
