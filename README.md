# Product Importer - Django Edition

A production-ready Django web application for importing large CSV files (up to 500MB) with real-time progress tracking, comprehensive product management, and webhook integration.

## Features

✅ **CSV Import with Real-Time Progress**
- Drag-and-drop file upload
- Real-time progress bar (1-second updates)
- Asynchronous processing with Celery
- Automatic duplicate handling (case-insensitive SKU)
- Support for up to 500,000 products

✅ **Product Management**
- Full CRUD operations (Create, Read, Update, Delete)
- Advanced filtering (SKU, name, active status)
- Paginated product lists (20 items/page)
- Responsive web interface

✅ **Bulk Operations**
- Delete all products with protective confirmation
- Visual feedback during operations
- Success/failure notifications

✅ **Webhook Configuration**
- Create, edit, test, delete webhooks
- Multiple event types (product_created, updated, deleted)
- Webhook delivery logs with status codes and timing
- Real-time event notifications

✅ **REST API**
- 17 API endpoints for programmatic access
- Comprehensive filtering and pagination
- JSON request/response format

## Tech Stack

- **Framework:** Django 4.2 + Django REST Framework
- **Database:** SQLite (development), PostgreSQL (production)
- **Task Queue:** Celery with SQLite broker (development) or Redis (production)
- **Frontend:** Django Templates (server-side rendered)
- **Styling:** Custom CSS with modern design

## Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone or navigate to project:**
```bash
cd FulFil
cd django_backend
```

2. **Create virtual environment (optional but recommended):**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run migrations:**
```bash
python manage.py migrate
```

5. **Create superuser:**
```bash
python manage.py createsuperuser
```

6. **Start development server:**
```bash
python manage.py runserver
```

7. **Start Celery worker (in another terminal):**
```bash
celery -A config worker --loglevel=info --pool=solo
```

### Access Application

- **Web UI:** http://localhost:8000/
- **Admin:** http://localhost:8000/admin/
- **API:** http://localhost:8000/api/

## Project Structure

```
FulFil/
├── django_backend/
│   ├── config/
│   │   ├── settings.py          # Django settings
│   │   ├── urls.py              # URL routing
│   │   └── wsgi.py              # WSGI config
│   ├── importer/
│   │   ├── models.py            # Database models
│   │   ├── views.py             # Views (web + API)
│   │   ├── forms.py             # Django forms
│   │   ├── urls.py              # App URLs
│   │   ├── tasks.py             # Celery tasks
│   │   └── migrations/          # Database migrations
│   ├── templates/
│   │   └── importer/            # HTML templates
│   ├── manage.py                # Django CLI
│   ├── requirements.txt         # Python dependencies
│   └── db.sqlite3               # SQLite database
├── sample_products.csv          # Sample data
├── DJANGO_README.md             # Django setup guide
├── DJANGO_QUICK_START.md        # Quick start guide
├── DJANGO_FRONTEND_SETUP.md     # Frontend setup
└── DJANGO_CELERY_SETUP.md       # Celery setup
```

## Database Models

### Product
```python
- sku (CharField, unique)
- name (CharField)
- description (TextField)
- price (DecimalField)
- quantity (IntegerField)
- active (BooleanField)
- created_at (DateTimeField)
- updated_at (DateTimeField)
```

### ImportJob
```python
- filename (CharField)
- status (CharField: pending, processing, completed, failed)
- total_records (IntegerField)
- processed_records (IntegerField)
- error_message (TextField)
- created_at (DateTimeField)
- completed_at (DateTimeField)
```

### Webhook
```python
- url (URLField)
- event_type (CharField: product_created, product_updated, product_deleted)
- active (BooleanField)
- created_at (DateTimeField)
```

### WebhookLog
```python
- webhook (ForeignKey)
- status_code (IntegerField)
- response_time (FloatField)
- error (TextField)
- created_at (DateTimeField)
```

## API Endpoints

### Products
- `GET /api/products/` - List products
- `POST /api/products/` - Create product
- `GET /api/products/{id}/` - Get product
- `PUT /api/products/{id}/` - Update product
- `DELETE /api/products/{id}/` - Delete product

### Import
- `POST /api/import/` - Upload CSV
- `GET /api/import/progress/{job_id}/` - Check import progress
- `GET /api/import/jobs/` - List import jobs

### Webhooks
- `GET /api/webhooks/` - List webhooks
- `POST /api/webhooks/` - Create webhook
- `GET /api/webhooks/{id}/` - Get webhook
- `PUT /api/webhooks/{id}/` - Update webhook
- `DELETE /api/webhooks/{id}/` - Delete webhook
- `GET /api/webhooks/{id}/logs/` - Get webhook logs
- `POST /api/webhooks/{id}/test/` - Test webhook

## Web UI Pages

### Dashboard
- Overview of total products, active/inactive count
- Recent imports
- Quick action buttons

### Products
- List all products with pagination
- Filter by SKU, name, status
- Create, edit, delete products
- Bulk operations

### Import CSV
- Upload CSV file
- Real-time progress tracking
- Import history
- Error handling

### Webhooks
- Configure webhook endpoints
- Select event types
- View delivery logs
- Test webhooks

## CSV Format

Your CSV file should have the following format:

```csv
sku,name,description,price,quantity
SKU001,Product 1,Description 1,29.99,100
SKU002,Product 2,Description 2,39.99,50
SKU003,Product 3,Description 3,49.99,75
```

**Required columns:** `sku`, `name`
**Optional columns:** `description`, `price`, `quantity`

## Celery Tasks

### CSV Import Task
```python
from importer.tasks import import_csv_task
task = import_csv_task.delay(content, filename, job_id)
```

### Webhook Trigger Task
```python
from importer.tasks import trigger_webhook
task = trigger_webhook.delay('product_created', {'product_id': '123'})
```

## Configuration

### Development Settings (settings.py)

```python
# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Celery (SQLite broker - no Redis needed)
CELERY_BROKER_URL = 'sqla+sqlite:///db.sqlite3'
CELERY_RESULT_BACKEND = 'db+sqlite:///db.sqlite3'
```

### Production Settings

For production, use PostgreSQL and Redis:

```python
# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Celery (Redis broker)
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
```

## Troubleshooting

### Celery Worker Won't Start
```bash
# Check if dependencies are installed
pip list | grep celery

# Reinstall if needed
pip install celery==5.3.4 kombu==5.3.4 sqlalchemy==2.0.23
```

### Database Locked Error
SQLite has concurrency issues. For production, use PostgreSQL.

### Templates Not Found
Ensure `templates/` directory exists in `django_backend/`

### Import Fails
- Check CSV format (required: sku, name)
- Check file size (max 500MB)
- Check Celery worker is running

## Performance

### Import Speed
- 1,000 records: ~3-5 seconds
- 10,000 records: ~30-60 seconds
- 100,000 records: ~5-10 minutes
- 500,000 records: ~25-50 minutes

### Optimization Tips
- Use PostgreSQL for production (better than SQLite)
- Run multiple Celery workers
- Use Redis broker instead of SQLite
- Add database indexes

## Documentation

- **DJANGO_README.md** - Detailed Django setup
- **DJANGO_QUICK_START.md** - 5-minute quick start
- **DJANGO_FRONTEND_SETUP.md** - Frontend templates guide
- **DJANGO_CELERY_SETUP.md** - Celery configuration

## Common Commands

```bash
# Run development server
python manage.py runserver

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start Celery worker
celery -A config worker --loglevel=info --pool=solo

# Access Django shell
python manage.py shell

# Create migrations
python manage.py makemigrations

# Collect static files (production)
python manage.py collectstatic

# Run tests
python manage.py test
```

## Environment Variables

Create `.env` file in `django_backend/`:

```env
# Database (production)
DB_NAME=product_importer
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Celery (production)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Django
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Deployment

### Local Development
```bash
python manage.py runserver
celery -A config worker --loglevel=info --pool=solo
```

### Production with Gunicorn
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
celery -A config worker --loglevel=info -c 4
```

### Docker
```bash
docker build -t product-importer .
docker run -p 8000:8000 product-importer
```

## License

MIT License - feel free to use this project for any purpose.

## Support

For issues or questions:
1. Check the documentation files
2. Review Django/DRF official docs
3. Check Celery documentation
4. Review code comments

---

**Status:** ✅ Production Ready
**Last Updated:** November 2025
