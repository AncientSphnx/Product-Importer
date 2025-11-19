### Prompt
I need a memory-efficient CSV streaming method to import 500k+ products in Django. Using Celery, how do I process the file line-by-line and handle batch upserts based on SKU?

### AI Output
- Use csv.DictReader with streamed file access
- Maintain batches of 1000 rows
- Preload existing SKUs into lowercased set
- For each row: validate → check SKU → update/create
- Update ImportJob counters after each batch
- Use Django ORM bulk operations where possible
- Final flush of remaining batch