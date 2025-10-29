# Market Trends Analysis API

FastAPI-based REST API for analyzing market trends and generating reports for companies.

## Features

- **Single Company Analysis**: Analyze one company at a time
- **Batch Analysis**: Process multiple companies in one request
- **Async Processing**: Jobs run in background threads
- **Status Tracking**: Monitor progress of analysis jobs
- **File Downloads**: Access generated reports (PDF, Markdown, JSON)

## Installation

Ensure you have all dependencies installed:

```bash
pip install fastapi uvicorn python-multipart
```

## Running the API

### Development Mode

```bash
# From the project root
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Or directly:

```bash
cd backend
python main.py
```

### Production Mode

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Root Endpoint

```bash
GET /
```

Returns API information and available endpoints.

**Example:**
```bash
curl http://localhost:8000/
```

### Health Check

```bash
GET /health
```

Returns service health status.

**Example:**
```bash
curl http://localhost:8000/health
```

### Analyze Single Company

```bash
POST /api/analyze
```

Start analysis for a single company.

**Request Body:**
```json
{
  "company_name": "Tesla",
  "company_linkedin": "https://linkedin.com/company/tesla-motors"
}
```

Note: `company_linkedin` is optional. You can also use the format: `"Tesla | https://linkedin.com/company/tesla-motors"`

**Example:**
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Tesla",
    "company_linkedin": "https://linkedin.com/company/tesla-motors"
  }'
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "company_name": "Tesla",
  "created_at": "2025-10-20T10:30:00",
  "message": "Analysis started for Tesla"
}
```

### Batch Analysis

```bash
POST /api/batch-analyze
```

Start analysis for multiple companies.

**Request Body:**
```json
{
  "companies": [
    {
      "name": "Tesla",
      "url_linkedin": "https://linkedin.com/company/tesla-motors",
      "url_sito": "https://www.tesla.com",
      "nazione": "USA",
      "citta": "Austin",
      "settore": "Automotive",
      "tipo_azienda": "multinazionale"
    },
    {
      "name": "OpenAI",
      "url_linkedin": "https://linkedin.com/company/openai",
      "url_sito": "https://www.openai.com",
      "nazione": "USA",
      "citta": "San Francisco",
      "settore": "AI",
      "tipo_azienda": "startup"
    }
  ]
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/batch-analyze \
  -H "Content-Type: application/json" \
  -d '{
    "companies": [
      {
        "name": "Tesla",
        "url_linkedin": "https://linkedin.com/company/tesla-motors",
        "url_sito": "https://www.tesla.com",
        "nazione": "USA",
        "citta": "Austin",
        "settore": "Automotive",
        "tipo_azienda": "multinazionale"
      }
    ]
  }'
```

**Response:**
```json
{
  "batch_id": "660e8400-e29b-41d4-a716-446655440000",
  "total_companies": 3,
  "jobs": [
    {
      "job_id": "770e8400-e29b-41d4-a716-446655440001",
      "status": "pending",
      "company_name": "Tesla",
      "created_at": "2025-10-20T10:30:00",
      "message": "Analysis queued for Tesla"
    },
    ...
  ],
  "message": "Batch analysis started for 3 companies"
}
```

### Check Analysis Status

```bash
GET /api/status/{job_id}
```

Get the status of an analysis job.

**Example:**
```bash
curl http://localhost:8000/api/status/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "company_name": "Tesla",
  "created_at": "2025-10-20T10:30:00",
  "started_at": "2025-10-20T10:30:01",
  "completed_at": "2025-10-20T10:32:30",
  "error_message": null,
  "progress": "Analysis completed successfully",
  "files": {
    "markdown_file": "outputs/executive_analysis_tesla_20251020_103000.md",
    "json_file": "outputs/structured_analysis_tesla_20251020_103000.json",
    "pdf_file": "outputs/structured_analysis_tesla_20251020_103000.pdf",
    "research_file": "outputs/research_results_tesla_20251020_103000.json",
    "images_count": 5
  }
}
```

**Status Values:**
- `pending`: Job created, not yet started
- `running`: Analysis in progress
- `completed`: Analysis finished successfully
- `failed`: Analysis failed (check error_message)

### List All Jobs

```bash
GET /api/jobs
```

List all analysis jobs.

**Example:**
```bash
curl http://localhost:8000/api/jobs
```

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440000",
      "company_name": "Tesla",
      "status": "completed",
      ...
    },
    ...
  ]
}
```

### Download Files

```bash
GET /api/download/{job_id}/{file_type}
```

Download a generated file from a completed analysis.

**File Types:**
- `markdown`: Executive analysis in Markdown format
- `json`: Structured analysis data
- `pdf`: PDF report (if successfully generated)
- `research`: Raw research results from Perplexity

**Example:**
```bash
# Download PDF report
curl -O http://localhost:8000/api/download/550e8400-e29b-41d4-a716-446655440000/pdf

# Download JSON data
curl -O http://localhost:8000/api/download/550e8400-e29b-41d4-a716-446655440000/json

# Download Markdown report
curl -O http://localhost:8000/api/download/550e8400-e29b-41d4-a716-446655440000/markdown
```

## Complete Workflow Example

```bash
# 1. Start analysis
RESPONSE=$(curl -s -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"company_name": "Tesla"}')

# 2. Extract job_id
JOB_ID=$(echo $RESPONSE | jq -r '.job_id')
echo "Job ID: $JOB_ID"

# 3. Poll for status (every 10 seconds)
while true; do
  STATUS=$(curl -s http://localhost:8000/api/status/$JOB_ID | jq -r '.status')
  echo "Status: $STATUS"

  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    break
  fi

  sleep 10
done

# 4. Download PDF report if completed
if [ "$STATUS" = "completed" ]; then
  curl -O http://localhost:8000/api/download/$JOB_ID/pdf
  echo "Report downloaded!"
fi
```

## Python Client Example

```python
import requests
import time

BASE_URL = "http://localhost:8000"

# 1. Start analysis
response = requests.post(
    f"{BASE_URL}/api/analyze",
    json={"company_name": "Tesla"}
)
job_id = response.json()["job_id"]
print(f"Job ID: {job_id}")

# 2. Poll for completion
while True:
    status_response = requests.get(f"{BASE_URL}/api/status/{job_id}")
    status = status_response.json()["status"]
    progress = status_response.json().get("progress", "")

    print(f"Status: {status} - {progress}")

    if status in ["completed", "failed"]:
        break

    time.sleep(10)

# 3. Download files if completed
if status == "completed":
    files = status_response.json()["files"]

    # Download PDF
    pdf_response = requests.get(f"{BASE_URL}/api/download/{job_id}/pdf")
    with open("report.pdf", "wb") as f:
        f.write(pdf_response.content)

    print("Report downloaded successfully!")
```

## Interactive API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to test all endpoints directly from your browser.

## Environment Variables

Ensure your `.env` file contains:

```env
PERPLEXITY_API_KEY=your_perplexity_key
ANTHROPIC_API_KEY=your_anthropic_key
```

## Output Directory

All generated files are saved in the `outputs/` directory by default. This includes:

- Markdown reports
- JSON data files
- PDF reports
- Research results
- Downloaded images

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (e.g., invalid input, job not completed)
- `404`: Resource not found (job_id or file)
- `500`: Internal server error

Error responses include a `detail` field with more information:

```json
{
  "detail": "Job not found"
}
```

## Performance Notes

- Analyses run in background threads, allowing the API to handle multiple requests
- Average analysis time: 2-5 minutes per company
- API remains responsive while jobs are processing
- Consider rate limiting for production use

## Integration with Original Scripts

This API wraps the functionality of:
- `get_trends.py`: Single company analysis
- `main.py`: Batch processing

The original CLI scripts still work independently if needed.
