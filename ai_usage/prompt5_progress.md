### Prompt
How can I implement a real-time progress API endpoint that the frontend can poll every second? What fields should it return?

### AI Output
- Use DRF APIView
- Return:
  - status
  - processed_records
  - total_records
  - percentage
  - error_message
- Example response:
```
{ "status": "processing", "processed_records": 12000, "total_records": 500000, "percentage": 2.4 }
```
- Frontend uses setInterval for polling