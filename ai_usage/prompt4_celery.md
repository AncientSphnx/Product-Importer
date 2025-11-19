### Prompt
How do I structure a Celery task for CSV processing? It should accept ImportJob ID, update status, iterate CSV in chunks, update progress, and mark job complete/failed.

### AI Output
- Use @shared_task
- Load ImportJob, set status=processing
- Wrap import logic in try/except
- Update processed_records inside loop
- On success: status=completed, set completed_at
- On failure: status=failed, store error_message
- Save job state frequently