"""
API Models for the market trends analysis service
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AnalysisStatus(str, Enum):
    """Status of an analysis job"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EnumTipoAzienda(str, Enum):
    """Type of company"""
    STARTUP = "startup"
    PMI = "pmi"
    GRANDE_IMPRESA = "grande_impresa"
    MULTINAZIONALE = "multinazionale"


class CompanyInfo(BaseModel):
    """Complete company information"""
    name: str = Field(..., description="Name of the company")
    url_linkedin: str = Field(..., description="LinkedIn URL of the company")
    url_sito: str = Field(..., description="Company website URL")
    nazione: str = Field(..., description="Country where the company is based")
    citta: str = Field(..., description="City where the company is based")
    settore: str = Field(..., description="Industry sector of the company")
    tipo_azienda: EnumTipoAzienda = Field(..., description="Type/size of the company")


class CompanyAnalysisRequest(BaseModel):
    """Request model for single company analysis"""
    company_info: CompanyInfo = Field(..., description="Complete company information")


class BatchAnalysisRequest(BaseModel):
    """Request model for batch company analysis"""
    companies: List[CompanyInfo] = Field(..., description="List of company information objects")


class AnalysisResponse(BaseModel):
    """Response model for analysis submission"""
    job_id: str = Field(..., description="Unique identifier for the analysis job")
    status: AnalysisStatus = Field(..., description="Current status of the job")
    company_name: str = Field(..., description="Company being analyzed")
    created_at: datetime = Field(default_factory=datetime.now, description="Job creation timestamp")
    message: str = Field(..., description="Status message")


class AnalysisStatusResponse(BaseModel):
    """Response model for checking analysis status"""
    job_id: str
    status: AnalysisStatus
    company_name: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    progress: Optional[str] = None
    files: Optional[dict] = None


class AnalysisFilesInfo(BaseModel):
    """Information about generated analysis files"""
    markdown_file: Optional[str] = None
    json_file: Optional[str] = None
    pdf_file: Optional[str] = None
    research_file: Optional[str] = None
    images_count: int = 0


class BatchAnalysisResponse(BaseModel):
    """Response model for batch analysis submission"""
    batch_id: str
    total_companies: int
    jobs: List[AnalysisResponse]
    message: str
