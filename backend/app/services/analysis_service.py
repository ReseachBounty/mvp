"""
Background analysis service that manages the execution of company analysis jobs
"""
import sys
import json
import os
import logging
import time
import uuid as uuid_lib
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
import threading
from dotenv import load_dotenv
from sqlmodel import Session

# Add parent directories to path to import from src
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from .api_clients import PerplexityClient, ClaudeClient
from .utils import (
    make_filename_safe,
    get_company_linkedin,
    detect_generic_analysis
)
from .report_generator import (
    clean_analysis_data,
    format_structured_output,
    convert_markdown_to_pdf
)
from .logging_config import setup_logging, get_context_logger
from ..models import TaskStatusEnum, CompanyInfo, Task
from .models import StructuredAnalysis
from ..core.db import engine
from .mock_data import get_mock_perplexity_response, get_mock_claude_response

# Load environment variables
load_dotenv()

# Check if dev mode is enabled
DEV_MODE = os.getenv('DEV_MODE', 'false').lower() == 'true'

# Configure structured logging
setup_logging(
    log_level=os.getenv('LOG_LEVEL', 'INFO'),
    use_json=os.getenv('USE_JSON_LOGS', 'true').lower() == 'true',
    log_file=os.getenv('LOG_FILE', None)
)

logger = logging.getLogger("analysis_service")

if DEV_MODE:
    logger.warning("=" * 80)
    logger.warning("DEV MODE ENABLED - Using mock data instead of real API calls")
    logger.warning("Set DEV_MODE=false in .env to use real APIs")
    logger.warning("=" * 80)


class AnalysisJob:
    """Represents a single analysis job"""

    def __init__(self, job_id: str, company_info: CompanyInfo, task_id: Optional[str] = None):
        self.job_id = job_id
        self.company_info = company_info
        self.task_id = task_id  # Database task ID for status updates
        self.status = TaskStatusEnum.PENDING
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.progress: Optional[str] = None
        self.files: Optional[Dict] = None

    @property
    def company_name(self) -> str:
        """Get company name from company_info"""
        return self.company_info.name

    def to_dict(self):
        """Convert job to dictionary"""
        return {
            "job_id": self.job_id,
            "company_name": self.company_info.name,
            "company_info": {
                "name": self.company_info.name,
                "url_linkedin": self.company_info.url_linkedin,
                "url_sito": self.company_info.url_sito,
                "nazione": self.company_info.nazione,
                "citta": self.company_info.citta,
                "settore": self.company_info.settore,
                "tipo_azienda": self.company_info.tipo_azienda.value
            },
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "progress": self.progress,
            "files": self.files
        }


class AnalysisService:
    """Service for managing analysis jobs"""

    def __init__(self, output_dir: str = "outputs"):
        self.jobs: Dict[str, AnalysisJob] = {}
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self._lock = threading.Lock()

        # Check API keys (not required in dev mode)
        self.perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')

        if not DEV_MODE:
            if not self.perplexity_api_key:
                logging.error("PERPLEXITY_API_KEY not found in environment variables")
                raise ValueError("PERPLEXITY_API_KEY not configured")

            if not self.anthropic_api_key:
                logging.error("ANTHROPIC_API_KEY not found in environment variables")
                raise ValueError("ANTHROPIC_API_KEY not configured")
        else:
            logging.info("DEV MODE: API keys not required")

    def create_job(self, company_info: CompanyInfo, task_id: Optional[str] = None) -> str:
        """Create a new analysis job

        Args:
            company_info: Company information for analysis
            task_id: Optional database task ID for status updates

        Returns:
            job_id: Unique identifier for this analysis job
        """
        job_id = str(uuid_lib.uuid4())

        log = get_context_logger(job_id=job_id, company_name=company_info.name)
        log.info("Creating new analysis job",
                 status=TaskStatusEnum.PENDING.value,
                 task_id=task_id,
                 step="job_creation")

        job = AnalysisJob(job_id, company_info, task_id)

        with self._lock:
            self.jobs[job_id] = job
            active_jobs = len([j for j in self.jobs.values() if j.status == TaskStatusEnum.RUNNING])

        log.info("Job created and queued",
                 status=TaskStatusEnum.PENDING.value,
                 active_jobs=active_jobs,
                 total_jobs=len(self.jobs))

        # Start analysis in background thread
        thread = threading.Thread(target=self._run_analysis, args=(job_id,), name=f"analysis-{job_id[:8]}")
        thread.daemon = True
        thread.start()

        log.info("Background thread started",
                 thread_name=thread.name,
                 thread_id=thread.ident)

        return job_id

    def get_job(self, job_id: str) -> Optional[AnalysisJob]:
        """Get job by ID"""
        with self._lock:
            return self.jobs.get(job_id)

    def list_jobs(self) -> list:
        """List all jobs"""
        with self._lock:
            return [job.to_dict() for job in self.jobs.values()]

    def _update_task_in_db(self, job: AnalysisJob):
        """Update task status in database if task_id is provided"""
        if not job.task_id:
            return

        try:
            with Session(engine) as session:
                task = session.get(Task, job.task_id)
                if task:
                    task.status = job.status.value
                    if job.error_message:
                        task.error_message = job.error_message
                    if job.files:
                        task.result_data = job.files
                    session.commit()
                    logger.debug(f"Updated task {job.task_id} in database with status {job.status.value}")
                else:
                    logger.warning(f"Task {job.task_id} not found in database")
        except Exception as e:
            logger.error(f"Error updating task {job.task_id} in database: {e}", exc_info=True)

    def _build_structured_result_data(
        self,
        analysis_json: Dict,
        pdf_path: Optional[Path],
        images_dir: Optional[Path]
    ) -> Dict:
        """
        Build structured result_data for the task

        Args:
            analysis_json: Parsed JSON analysis from Claude
            pdf_path: Path to generated PDF file
            images_dir: Directory containing downloaded images

        Returns:
            Structured dictionary with overview, actions, analytics, and bytes
        """
        result_data = {
            "overview": {},
            "actions": {},
            "analytics": {
                "images": []
            },
            "bytes": None
        }

        try:
            # Extract overview from executive_summary
            if "executive_summary" in analysis_json:
                result_data["overview"] = analysis_json["executive_summary"]

            # Extract actions from strategic_recommendations
            if "strategic_recommendations" in analysis_json:
                result_data["actions"] = analysis_json["strategic_recommendations"]

            # Collect image paths from images directory
            if images_dir and images_dir.exists():
                image_files = []
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif']:
                    image_files.extend(images_dir.glob(ext))

                result_data["analytics"]["images"] = [
                    str(img_path.absolute()) for img_path in sorted(image_files)
                ]

                logger.info(f"Collected {len(image_files)} images from {images_dir}")

            # Read PDF and convert to base64
            if pdf_path and pdf_path.exists():
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_bytes = pdf_file.read()
                    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
                    result_data["bytes"] = pdf_base64

                logger.info(f"Converted PDF to base64 ({len(pdf_base64)} characters)")
            else:
                logger.warning("PDF file not found, bytes field will be null")

        except Exception as e:
            logger.error(f"Error building structured result data: {e}", exc_info=True)

        return result_data

    def _run_analysis(self, job_id: str):
        """Run the analysis pipeline for a job"""
        # Initialize timing
        pipeline_start = time.time()

        job = self.get_job(job_id)
        if not job:
            logger.error(f"Job {job_id} not found - cannot run analysis")
            return

        log = get_context_logger(job_id=job_id, company_name=job.company_name)

        try:
            log.info("Analysis thread started",
                     thread_name=threading.current_thread().name,
                     step="thread_start")

            # Update status to RUNNING
            old_status = job.status
            job.status = TaskStatusEnum.RUNNING
            job.started_at = datetime.now()
            job.progress = "Initializing analysis"

            # Save status to database
            self._update_task_in_db(job)

            log.info("Status transition: PENDING → RUNNING",
                     old_status=old_status.value,
                     new_status=TaskStatusEnum.RUNNING.value,
                     status=TaskStatusEnum.RUNNING.value,
                     step="status_change")

            company_info = job.company_info
            company_name = company_info.name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            company_name_safe = make_filename_safe(company_name)

            log.info("Starting analysis pipeline",
                     company_name=company_name,
                     linkedin=company_info.url_linkedin,
                     website=company_info.url_sito,
                     country=company_info.nazione,
                     city=company_info.citta,
                     sector=company_info.settore,
                     company_type=company_info.tipo_azienda.value,
                     step="pipeline_start")

            # Step 1: Research with Perplexity
            step1_start = time.time()
            job.progress = "Conducting market research"

            log.info("STEP 1/3: Starting market research with Perplexity AI",
                     step="research_start",
                     progress="1/3",
                     dev_mode=DEV_MODE)

            if DEV_MODE:
                log.info("DEV MODE: Using mock Perplexity data")
                # Simulate API delay
                time.sleep(2)
                research_results = get_mock_perplexity_response(
                    company_name=company_name,
                    company_type=company_info.tipo_azienda.value
                )
            else:
                perplexity = PerplexityClient(self.perplexity_api_key)
                log.info("Calling Perplexity API for company research")
                research_results = perplexity.research_company(
                    company_name=company_name,
                    company_linkedin=company_info.url_linkedin,
                    company_website=company_info.url_sito,
                    country=company_info.nazione,
                    city=company_info.citta,
                    sector=company_info.settore,
                    company_type=company_info.tipo_azienda.value
                )

            step1_duration = int((time.time() - step1_start) * 1000)

            log.info("Perplexity research completed, saving results",
                     duration_ms=step1_duration,
                     dev_mode=DEV_MODE,
                     step="research_api_complete")

            # Save research results
            perplexity_filename = self.output_dir / f"research_results_{company_name_safe}_{timestamp}.json"
            with open(perplexity_filename, 'w', encoding='utf-8') as f:
                json.dump(research_results, f, indent=4)

            log.info("Research results saved to disk",
                     file=str(perplexity_filename),
                     file_size=perplexity_filename.stat().st_size,
                     duration_ms=step1_duration,
                     step="research_complete")

            # Check for critical failures
            log.info("Validating research results")

            perplexity_content = research_results.get('choices', [{}])[0].get('message', {}).get('content', '')

            log.info("Research content extracted",
                     content_length=len(perplexity_content),
                     step="research_validation")

            critical_failures = [
                'cannot find any information',
                'no data available',
                'company does not exist',
                'ANALYSIS NOT POSSIBLE'
            ]

            failures_found = [f for f in critical_failures if f in perplexity_content]
            if failures_found:
                log.error("Critical failures detected in research results",
                         failures=failures_found,
                         step="research_validation_failed")
                raise ValueError(f"Insufficient data found for company analysis: {', '.join(failures_found)}")

            log.info("Research validation passed",
                     step="research_validated")

            # Step 2: Analyze with Claude
            step2_start = time.time()
            job.progress = "Analyzing data with AI"

            log.info("STEP 2/3: Starting data analysis with Claude AI",
                     step="analysis_start",
                     progress="2/3",
                     dev_mode=DEV_MODE)

            if DEV_MODE:
                log.info("DEV MODE: Using mock Claude data")
                # Simulate API delay
                time.sleep(3)
                analysis_text = get_mock_claude_response(company_name=company_name)
            else:
                claude = ClaudeClient(self.anthropic_api_key)
                log.info("Calling Claude API for analysis")
                analysis_text = claude.analyze_research(
                    company_name=company_name,
                    research_data=research_results,
                    company_info=company_info
                )

            step2_duration = int((time.time() - step2_start) * 1000)

            log.info("Claude analysis completed, parsing JSON",
                     duration_ms=step2_duration,
                     response_length=len(analysis_text),
                     dev_mode=DEV_MODE,
                     step="analysis_api_complete")

            # Parse and validate
            try:
                analysis_json = json.loads(analysis_text)
                log.info("JSON parsed successfully",
                         step="json_parsed")
            except json.JSONDecodeError as e:
                log.error("Failed to parse Claude response as JSON",
                         error=str(e),
                         response_preview=analysis_text[:500],
                         step="json_parse_failed",
                         exc_info=True)
                raise ValueError(f"Invalid JSON response from Claude: {e}")

            analysis_json_cleaned = clean_analysis_data(analysis_json)

            log.info("Analysis data cleaned",
                     step="data_cleaned")

            # Detect generic analysis
            log.info("Checking for generic analysis")

            is_generic, reason = detect_generic_analysis(analysis_json_cleaned)
            if is_generic:
                log.error("Analysis detected as too generic",
                         reason=reason,
                         step="generic_analysis_detected")
                raise ValueError(f"Analysis too generic: {reason}")

            log.info("Generic analysis check passed",
                     step="generic_check_passed")

            # Validate with Pydantic
            log.info("Validating analysis structure with Pydantic")

            try:
                structured_analysis = StructuredAnalysis(**analysis_json_cleaned)
                log.info("Pydantic validation passed",
                         step="pydantic_validated")
            except Exception as e:
                log.error("Pydantic validation failed",
                         error=str(e),
                         step="pydantic_validation_failed",
                         exc_info=True)
                raise

            log.info("Analysis step completed successfully",
                     duration_ms=step2_duration,
                     step="analysis_complete")

            # Step 3: Generate reports
            step3_start = time.time()
            job.progress = "Generating reports"

            log.info("STEP 3/3: Starting report generation",
                     step="report_generation_start",
                     progress="3/3")

            # Format output and download images
            log.info("Formatting structured output and downloading images")

            format_start = time.time()
            formatted_output, downloaded_images = format_structured_output(
                analysis_json_cleaned,
                company_name,
                timestamp,
                str(self.output_dir)
            )
            format_duration = int((time.time() - format_start) * 1000)

            log.info("Output formatted and images downloaded",
                     duration_ms=format_duration,
                     images_count=len(downloaded_images) if downloaded_images else 0,
                     output_length=len(formatted_output),
                     step="format_complete")

            # Save files
            log.info("Saving markdown file")

            markdown_filename = self.output_dir / f"executive_analysis_{company_name_safe}_{timestamp}.md"
            with open(markdown_filename, 'w', encoding='utf-8') as f:
                f.write(formatted_output)

            log.info("Markdown file saved",
                     file=str(markdown_filename),
                     file_size=markdown_filename.stat().st_size,
                     step="markdown_saved")

            log.info("Saving JSON file")

            json_filename = self.output_dir / f"structured_analysis_{company_name_safe}_{timestamp}.json"
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(analysis_json_cleaned, f, indent=2)

            log.info("JSON file saved",
                     file=str(json_filename),
                     file_size=json_filename.stat().st_size,
                     step="json_saved")

            # Convert to PDF
            log.info("Converting markdown to PDF")

            pdf_start = time.time()
            pdf_filename = self.output_dir / f"structured_analysis_{company_name_safe}_{timestamp}.pdf"
            images_dir = f"images_{timestamp}" if downloaded_images else None
            pdf_success = convert_markdown_to_pdf(
                formatted_output,
                str(pdf_filename),
                company_name,
                str(self.output_dir / images_dir) if images_dir else None
            )
            pdf_duration = int((time.time() - pdf_start) * 1000)

            if pdf_success:
                log.info("PDF generated successfully",
                         duration_ms=pdf_duration,
                         file=str(pdf_filename),
                         file_size=pdf_filename.stat().st_size,
                         step="pdf_generated")
            else:
                log.warning("PDF generation failed",
                           duration_ms=pdf_duration,
                           step="pdf_failed")

            step3_duration = int((time.time() - step3_start) * 1000)
            log.info("Report generation completed",
                     duration_ms=step3_duration,
                     step="report_generation_complete")

            # Build structured result_data with overview, actions, analytics, and PDF bytes
            log.info("Building structured result data")

            images_directory = self.output_dir / images_dir if images_dir else None

            job.files = self._build_structured_result_data(
                analysis_json=analysis_json_cleaned,
                pdf_path=pdf_filename if pdf_success else None,
                images_dir=images_directory
            )

            log.info("Structured result data created",
                     has_overview="overview" in job.files and bool(job.files["overview"]),
                     has_actions="actions" in job.files and bool(job.files["actions"]),
                     images_count=len(job.files.get("analytics", {}).get("images", [])),
                     has_pdf_bytes=bool(job.files.get("bytes")),
                     step="result_data_structured")

            # Update status to COMPLETED
            old_status = job.status
            job.status = TaskStatusEnum.COMPLETED
            job.completed_at = datetime.now()
            job.progress = "Analysis completed successfully"

            # Save final status and results to database
            self._update_task_in_db(job)

            total_elapsed = (job.completed_at - job.started_at).total_seconds()
            pipeline_elapsed = (time.time() - pipeline_start)

            log.info("Status transition: RUNNING → COMPLETED",
                     old_status=old_status.value,
                     new_status=TaskStatusEnum.COMPLETED.value,
                     status=TaskStatusEnum.COMPLETED.value,
                     step="status_change")

            log.info("✓ SUCCESS - Analysis pipeline completed",
                     total_duration_seconds=round(total_elapsed, 2),
                     pipeline_duration_seconds=round(pipeline_elapsed, 2),
                     step1_duration_ms=step1_duration,
                     step2_duration_ms=step2_duration,
                     step3_duration_ms=step3_duration,
                     step="pipeline_success")

        except Exception as e:
            # Calculate elapsed time even for failures
            if job.started_at:
                elapsed = (datetime.now() - job.started_at).total_seconds()
            else:
                elapsed = 0

            # Update job status
            old_status = job.status
            job.status = TaskStatusEnum.FAILED
            job.completed_at = datetime.now()
            job.error_message = str(e)
            job.progress = "Analysis failed"

            # Save error status to database
            self._update_task_in_db(job)

            # Determine error type
            error_type = type(e).__name__

            log.error("✗ FAILURE - Analysis pipeline failed",
                     old_status=old_status.value,
                     new_status=TaskStatusEnum.FAILED.value,
                     status=TaskStatusEnum.FAILED.value,
                     error_type=error_type,
                     error_message=str(e),
                     elapsed_seconds=round(elapsed, 2),
                     step="pipeline_failed",
                     exc_info=True)

            # Log additional context for common errors
            if "timeout" in str(e).lower():
                log.error("Timeout detected - API call took too long",
                         error_type="timeout")
            elif "connection" in str(e).lower():
                log.error("Connection error - network issue or API unavailable",
                         error_type="connection_error")
            elif "rate limit" in str(e).lower():
                log.error("Rate limit exceeded - too many API requests",
                         error_type="rate_limit")
            elif "json" in str(e).lower():
                log.error("JSON parsing error - invalid response format",
                         error_type="json_error")


# Singleton instance
_analysis_service: Optional[AnalysisService] = None


def get_analysis_service() -> AnalysisService:
    """Get or create the analysis service singleton"""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService()
    return _analysis_service
