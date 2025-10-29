"""
Client for communicating with the analysis service.
Provides methods to submit analysis jobs and check their status.
"""

import os
import requests
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel
from enum import Enum

logger = logging.getLogger(__name__)


class AnalysisStatus(str, Enum):
    """Status of an analysis job"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class CompanyInfoRequest(BaseModel):
    """Company info for analysis request"""
    name: str
    url_linkedin: Optional[str] = None
    url_sito: Optional[str] = None
    nazione: Optional[str] = None
    citta: Optional[str] = None
    settore: Optional[str] = None
    tipo_azienda: str = "startup"


class AnalysisJobResponse(BaseModel):
    """Response from analysis service"""
    job_id: str
    company_name: str
    status: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    progress: Optional[str] = None
    files: Optional[Dict[str, Any]] = None


class AnalysisServiceClient:
    """Client for the analysis service API"""

    def __init__(
        self,
        base_url: str = None,
        timeout: int = 30
    ):
        """
        Initialize analysis service client

        Args:
            base_url: Base URL of the analysis service (defaults to env variable)
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url or os.getenv('ANALYSIS_SERVICE_URL', 'http://localhost:8001')
        self.timeout = timeout

        logger.info(f"Analysis service client initialized with base_url={self.base_url}")

    def create_analysis(self, company_info: CompanyInfoRequest) -> str:
        """
        Submit a new analysis job

        Args:
            company_info: Company information for analysis

        Returns:
            Job ID

        Raises:
            requests.RequestException: If the request fails
        """
        url = f"{self.base_url}/api/analyze"

        payload = company_info.model_dump()

        logger.info(f"Submitting analysis job for company: {company_info.name}")
        logger.debug(f"Request payload: {payload}")

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout
            )

            response.raise_for_status()

            result = response.json()
            job_id = result.get('job_id')

            logger.info(f"Analysis job created successfully: {job_id}")

            return job_id

        except requests.Timeout as e:
            logger.error(f"Timeout submitting analysis job: {e}")
            raise

        except requests.RequestException as e:
            logger.error(f"Error submitting analysis job: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise

    def get_job_status(self, job_id: str) -> AnalysisJobResponse:
        """
        Get the status of an analysis job

        Args:
            job_id: Job ID to check

        Returns:
            Job status information

        Raises:
            requests.RequestException: If the request fails
        """
        url = f"{self.base_url}/api/status/{job_id}"

        logger.debug(f"Checking status for job: {job_id}")

        try:
            response = requests.get(
                url,
                timeout=self.timeout
            )

            response.raise_for_status()

            result = response.json()

            job_response = AnalysisJobResponse(**result)

            logger.debug(f"Job {job_id} status: {job_response.status}")

            return job_response

        except requests.Timeout as e:
            logger.error(f"Timeout checking job status: {e}")
            raise

        except requests.RequestException as e:
            logger.error(f"Error checking job status: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise

    def wait_for_completion(
        self,
        job_id: str,
        poll_interval: int = 5,
        max_wait: int = 600
    ) -> AnalysisJobResponse:
        """
        Wait for a job to complete (blocking)

        Args:
            job_id: Job ID to wait for
            poll_interval: Seconds between status checks (default: 5)
            max_wait: Maximum seconds to wait (default: 600)

        Returns:
            Final job status

        Raises:
            TimeoutError: If max_wait is exceeded
            ValueError: If job fails
        """
        import time

        logger.info(f"Waiting for job {job_id} to complete (max_wait={max_wait}s)")

        start_time = time.time()

        while True:
            elapsed = time.time() - start_time

            if elapsed > max_wait:
                logger.error(f"Job {job_id} exceeded max wait time of {max_wait}s")
                raise TimeoutError(f"Job {job_id} did not complete within {max_wait} seconds")

            job_status = self.get_job_status(job_id)

            if job_status.status == AnalysisStatus.COMPLETED:
                logger.info(f"Job {job_id} completed successfully")
                return job_status

            elif job_status.status == AnalysisStatus.FAILED:
                logger.error(f"Job {job_id} failed: {job_status.error_message}")
                raise ValueError(f"Job failed: {job_status.error_message}")

            else:
                logger.debug(
                    f"Job {job_id} still {job_status.status}, "
                    f"waiting {poll_interval}s... (elapsed: {elapsed:.1f}s)"
                )
                time.sleep(poll_interval)

    def health_check(self) -> bool:
        """
        Check if the analysis service is available

        Returns:
            True if service is healthy, False otherwise
        """
        try:
            # Try to access a simple endpoint
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Analysis service health check failed: {e}")
            return False
