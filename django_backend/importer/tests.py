"""Tests for importer app."""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import Product, ImportJob, Webhook


class ProductTestCase(TestCase):
    """Test cases for Product model."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.product = Product.objects.create(
            sku='TEST001',
            name='Test Product',
            price=29.99,
            quantity=100
        )

    def test_product_creation(self):
        """Test product creation."""
        self.assertEqual(self.product.sku, 'TEST001')
        self.assertEqual(self.product.name, 'Test Product')
        self.assertTrue(self.product.active)

    def test_sku_uppercase(self):
        """Test SKU is converted to uppercase."""
        product = Product.objects.create(
            sku='lowercase',
            name='Test'
        )
        self.assertEqual(product.sku, 'LOWERCASE')

    def test_duplicate_sku_rejected(self):
        """Test duplicate SKU is rejected."""
        with self.assertRaises(Exception):
            Product.objects.create(
                sku='TEST001',
                name='Duplicate'
            )

    def test_product_list_api(self):
        """Test product list API."""
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, 200)

    def test_product_create_api(self):
        """Test product creation via API."""
        data = {
            'sku': 'NEW001',
            'name': 'New Product',
            'price': 49.99,
            'quantity': 50
        }
        response = self.client.post('/api/products/', data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_product_update_api(self):
        """Test product update via API."""
        data = {'name': 'Updated Product'}
        response = self.client.patch(
            f'/api/products/{self.product.id}/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, 200)

    def test_product_delete_api(self):
        """Test product deletion via API."""
        response = self.client.delete(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, 204)


class WebhookTestCase(TestCase):
    """Test cases for Webhook model."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.webhook = Webhook.objects.create(
            url='https://example.com/webhook',
            event_type='product_created',
            active=True
        )

    def test_webhook_creation(self):
        """Test webhook creation."""
        self.assertEqual(self.webhook.event_type, 'product_created')
        self.assertTrue(self.webhook.active)

    def test_webhook_list_api(self):
        """Test webhook list API."""
        response = self.client.get('/api/webhooks/')
        self.assertEqual(response.status_code, 200)

    def test_webhook_create_api(self):
        """Test webhook creation via API."""
        data = {
            'url': 'https://example.com/webhook2',
            'event_type': 'product_updated',
            'active': True
        }
        response = self.client.post('/api/webhooks/', data, format='json')
        self.assertEqual(response.status_code, 201)
