### Prompt
I'm building a Django-based product importer tool that can process 500,000+ products from a CSV file with real-time progress updates. I need an overall system architecture: Django + Celery + PostgreSQL + Redis. Can you propose a clean folder structure, which Django apps I should create, and how to organize templates, API endpoints, and background tasks?

### AI Output
- Use Django 4.x + DRF for backend
- Create a main app called `importer` for models (Product, ImportJob, Webhook, WebhookLog)
- Create `config` project folder with Django + Celery settings
- Use Redis as broker in production
- Suggested structure:
```
django_backend/
  config/
  importer/
    models.py
    views.py
    tasks.py
    serializers.py
    templates/importer/
```
- DRF endpoints for products, imports, webhooks
- Celery processes CSV in chunks
- Use ImportJob for tracking progress