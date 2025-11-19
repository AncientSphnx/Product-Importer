### Prompt
How do I deploy Django + Celery on Render with Gunicorn web service and Celery background worker?

### AI Output
- Use render.yaml with two services:
  - Web → Gunicorn
  - Worker → Celery worker
- Required env vars:
  - DATABASE_URL
  - SECRET_KEY
  - DEBUG
  - CELERY_BROKER_URL
  - CELERY_RESULT_BACKEND
- Example start commands:
  - `gunicorn config.wsgi:application`
  - `celery -A config worker --loglevel=info`
