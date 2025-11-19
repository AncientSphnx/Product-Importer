### Prompt
I need Django models for Product, ImportJob, Webhook, and WebhookLog. Product needs SKU (unique, case-insensitive), name, description, price, quantity, and active. ImportJob tracks record counts and status. Webhook stores URL, event type, active flag. All should use UUID primary keys.

### AI Output
- Product model:
  - id (UUID)
  - sku (unique)
  - name, description
  - price, quantity
  - active
- ImportJob:
  - filename, status, total_records, processed_records, created_records, updated_records
- Webhook:
  - url, event_type, active
- WebhookLog:
  - webhook FK, status_code, response_time_ms, error_message
- Recommended indexes: SKU, created_at