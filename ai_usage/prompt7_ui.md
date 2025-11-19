### Prompt
I want Django template-based UI with vanilla JS. Pages needed: Dashboard, Product List, Import Page with progress bar, Webhook List. How should templates be structured?

### AI Output
- Use templates/importer directory
- Use base.html with sidebar + content blocks
- import.html:
  - file input
  - upload button
  - progress bar: <progress id="progress-bar">
  - JS polling to /api/import/progress/<job_id>
- product_list.html: table + pagination
- webhook_list.html: form + logs