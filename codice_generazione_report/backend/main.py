from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from pathlib import Path
import uuid

from backend.models import (
    CompanyAnalysisRequest,
    BatchAnalysisRequest,
    AnalysisResponse,
    AnalysisStatusResponse,
    BatchAnalysisResponse,
    AnalysisStatus
)
from backend.analysis_service import get_analysis_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = FastAPI(
    title="Market Trends Analysis API",
    description="API for analyzing market trends and generating reports for companies",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "message": "Market Trends Analysis API is running 🚀",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "analyze": "/api/analyze",
            "batch_analyze": "/api/batch-analyze",
            "status": "/api/status/{job_id}",
            "jobs": "/api/jobs",
            "download": "/api/download/{job_id}/{file_type}"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "analysis-api"}


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_company(request: CompanyAnalysisRequest):
    """
    Start analysis for a single company

    - **company_info**: Complete company information including:
        - **name**: Company name
        - **url_linkedin**: LinkedIn company page URL
        - **url_sito**: Company website URL
        - **nazione**: Country
        - **citta**: City
        - **settore**: Industry sector
        - **tipo_azienda**: Company type (startup, pmi, grande_impresa, multinazionale)
    """
    try:
        service = get_analysis_service()
        job_id = service.create_job(request.company_info)
        job = service.get_job(job_id)

        return AnalysisResponse(
            job_id=job_id,
            status=job.status,
            company_name=job.company_info.name,
            created_at=job.created_at,
            message=f"Analysis started for {job.company_info.name}"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Error creating analysis job: {e}")
        raise HTTPException(status_code=500, detail="Failed to start analysis")


@app.post("/api/batch-analyze", response_model=BatchAnalysisResponse)
async def batch_analyze_companies(request: BatchAnalysisRequest):
    """
    Start batch analysis for multiple companies

    - **companies**: List of CompanyInfo objects with complete company information
    """
    try:
        service = get_analysis_service()
        batch_id = str(uuid.uuid4())
        jobs = []

        for company in request.companies:
            job_id = service.create_job(company)
            job = service.get_job(job_id)

            jobs.append(AnalysisResponse(
                job_id=job_id,
                status=job.status,
                company_name=job.company_name,
                created_at=job.created_at,
                message=f"Analysis queued for {job.company_name}"
            ))

        return BatchAnalysisResponse(
            batch_id=batch_id,
            total_companies=len(jobs),
            jobs=jobs,
            message=f"Batch analysis started for {len(jobs)} companies"
        )

    except Exception as e:
        logging.error(f"Error creating batch analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to start batch analysis")


@app.get("/api/status/{job_id}", response_model=AnalysisStatusResponse)
async def get_analysis_status(job_id: str):
    """
    Get the status of an analysis job

    - **job_id**: The unique identifier of the analysis job
    """
    service = get_analysis_service()
    job = service.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return AnalysisStatusResponse(
        job_id=job.job_id,
        status=job.status,
        company_name=job.company_name,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error_message=job.error_message,
        progress=job.progress,
        files=job.files
    )


@app.get("/api/jobs")
async def list_jobs():
    """
    List all analysis jobs
    """
    service = get_analysis_service()
    return {"jobs": service.list_jobs()}


@app.get("/api/download/{job_id}/{file_type}")
async def download_file(job_id: str, file_type: str):
    """
    Download a generated file from a completed analysis

    - **job_id**: The unique identifier of the analysis job
    - **file_type**: Type of file to download (markdown, json, pdf, research)
    """
    service = get_analysis_service()
    job = service.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != AnalysisStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Job not completed yet")

    if not job.files:
        raise HTTPException(status_code=404, detail="No files available")

    # Map file types to file paths
    file_map = {
        "markdown": job.files.get("markdown_file"),
        "json": job.files.get("json_file"),
        "pdf": job.files.get("pdf_file"),
        "research": job.files.get("research_file")
    }

    file_path = file_map.get(file_type)

    if not file_path or not Path(file_path).exists():
        raise HTTPException(status_code=404, detail=f"File type '{file_type}' not found")

    # Determine media type
    media_types = {
        "markdown": "text/markdown",
        "json": "application/json",
        "pdf": "application/pdf",
        "research": "application/json"
    }

    return FileResponse(
        path=file_path,
        media_type=media_types.get(file_type, "application/octet-stream"),
        filename=Path(file_path).name
    )


if __name__ == "__main__":
    import uvicorn
    # Run on port 8001 to avoid conflict with main backend (port 8000)
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8001, reload=True)
