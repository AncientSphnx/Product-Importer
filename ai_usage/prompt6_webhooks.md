### Prompt
I need webhook CRUD and async execution. How do I send POST requests asynchronously and log results?

### AI Output
- Webhook CRUD via DRF
- Celery task for sending webhooks:
  - Include event_type + product/import data
  - Log response_code, response_time_ms, error_message
- Use requests.post with timeout
- Provide `/api/webhooks/<id>/test/` for manual test