"""Celery tasks for async processing."""
import csv
import io
import time
import requests
import logging
from celery import shared_task
from django.db.models import Q
from .models import Product, ImportJob, Webhook, WebhookLog

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def import_csv_task(self, file_content, filename, job_id):
    """
    Import CSV file asynchronously.
    
    Args:
        file_content: CSV file content as bytes
        filename: Original filename
        job_id: Import job ID
    """
    try:
        job = ImportJob.objects.get(id=job_id)
        job.status = 'processing'
        job.save()

        # Parse CSV
        csv_file = io.StringIO(file_content.decode('utf-8'))
        reader = csv.DictReader(csv_file)

        if not reader.fieldnames:
            raise ValueError("CSV file is empty or invalid")

        # Count total records
        csv_file.seek(0)
        total_records = sum(1 for _ in reader) - 1
        job.total_records = total_records
        job.save()

        # Reset reader
        csv_file.seek(0)
        reader = csv.DictReader(csv_file)

        created_count = 0
        updated_count = 0
        processed_count = 0

        # Process in chunks
        chunk_size = 1000
        products_to_create = []

        for row_num, row in enumerate(reader, 1):
            try:
                sku = row.get('sku', '').strip().upper()
                name = row.get('name', '').strip()
                description = row.get('description', '').strip()
                price = float(row.get('price', 0)) if row.get('price') else None
                quantity = int(row.get('quantity', 0)) if row.get('quantity') else 0

                if not sku or not name:
                    logger.warning(f"Row {row_num}: Missing SKU or name, skipping")
                    continue

                # Check if product exists (case-insensitive SKU)
                existing = Product.objects.filter(sku__iexact=sku).first()

                if existing:
                    # Update existing product
                    existing.name = name
                    existing.description = description
                    existing.price = price
                    existing.quantity = quantity
                    existing.save()
                    updated_count += 1
                    
                    # Trigger webhook
                    trigger_webhook.delay('product_updated', {'product_id': str(existing.id), 'sku': existing.sku})
                else:
                    # Create new product
                    product = Product(
                        sku=sku,
                        name=name,
                        description=description,
                        price=price,
                        quantity=quantity,
                        active=True
                    )
                    products_to_create.append(product)
                    created_count += 1

                processed_count += 1

                # Batch create
                if len(products_to_create) >= chunk_size:
                    Product.objects.bulk_create(products_to_create)
                    
                    # Trigger webhooks for created products
                    for product in products_to_create:
                        trigger_webhook.delay('product_created', {'product_id': str(product.id), 'sku': product.sku})
                    
                    products_to_create = []

                # Update progress every 100 records
                if processed_count % 100 == 0:
                    job.processed_records = processed_count
                    job.created_records = created_count
                    job.updated_records = updated_count
                    job.save()

                    # Update Celery task progress
                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'current': processed_count,
                            'total': total_records,
                            'status': f'Processing: {processed_count}/{total_records}'
                        }
                    )

            except Exception as e:
                logger.error(f"Error processing row {row_num}: {str(e)}")
                continue

        # Final batch create
        if products_to_create:
            Product.objects.bulk_create(products_to_create)
            
            # Trigger webhooks
            for product in products_to_create:
                trigger_webhook.delay('product_created', {'product_id': str(product.id), 'sku': product.sku})

        # Update job status
        job.status = 'completed'
        job.processed_records = processed_count
        job.created_records = created_count
        job.updated_records = updated_count
        job.save()

        logger.info(f"Import completed: {created_count} created, {updated_count} updated")

        return {
            'status': 'completed',
            'created': created_count,
            'updated': updated_count,
            'total': processed_count
        }

    except Exception as e:
        logger.error(f"Import task failed: {str(e)}")
        job.status = 'failed'
        job.error_message = str(e)
        job.save()
        raise


@shared_task
def trigger_webhook(event_type, payload):
    """
    Trigger webhook delivery.
    
    Args:
        event_type: Type of event
        payload: Event payload
    """
    try:
        webhooks = Webhook.objects.filter(active=True, event_type=event_type)

        for webhook in webhooks:
            try:
                start_time = time.time()

                response = requests.post(
                    webhook.url,
                    json={
                        'event_type': event_type,
                        'data': payload
                    },
                    timeout=10
                )

                response_time_ms = (time.time() - start_time) * 1000

                # Log webhook delivery
                log = WebhookLog(
                    webhook=webhook,
                    event_type=event_type,
                    status_code=response.status_code,
                    response_time_ms=response_time_ms
                )

                if response.status_code >= 400:
                    log.error_message = response.text[:500]

                log.save()

            except Exception as e:
                logger.error(f"Webhook trigger failed for {webhook.url}: {str(e)}")
                log = WebhookLog(
                    webhook=webhook,
                    event_type=event_type,
                    error_message=str(e)[:500]
                )
                log.save()

    except Exception as e:
        logger.error(f"Error triggering webhooks: {str(e)}")
        raise
