from fastapi import APIRouter, BackgroundTasks
import uuid
from typing import Any
import logging

from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.services.analysis_client import AnalysisServiceClient, CompanyInfoRequest
from app.models import CompanyInfo, TaskPublic, CompanyInfoCreate, Task, CompanyInfoBase
# from utils.email import generate_send_report_email, send_email
from typing import List

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/report", tags=["report"])


def poll_analysis_service(task_id: uuid.UUID, analysis_job_id: str, db_session: SessionDep):
    """
    Background task to poll the analysis service and update task status.

    Args:
        task_id: Database task ID
        analysis_job_id: Analysis service job ID
        db_session: Database session
    """
    import time
    from sqlmodel import Session
    from app.core.db import engine

    logger.info(f"Starting background polling for task {task_id}, job {analysis_job_id}")

    client = AnalysisServiceClient()

    # Poll interval and max wait time
    poll_interval = 10  # seconds
    max_wait = 600  # 10 minutes

    start_time = time.time()

    with Session(engine) as session:
        try:
            while True:
                elapsed = time.time() - start_time

                # Check if max wait exceeded
                if elapsed > max_wait:
                    logger.error(f"Task {task_id} polling exceeded max wait time")
                    task = session.get(Task, task_id)
                    if task:
                        task.status = "failed"
                        task.error_message = "Analysis timed out"
                        session.commit()
                    break

                # Get job status from analysis service
                try:
                    job_status = client.get_job_status(analysis_job_id)

                    logger.info(
                        f"Task {task_id}: Analysis job {analysis_job_id} status = {job_status.status}, "
                        f"progress = {job_status.progress}"
                    )

                    # Update task in database
                    task = session.get(Task, task_id)
                    if not task:
                        logger.error(f"Task {task_id} not found in database")
                        break

                    # Map analysis status to task status
                    if job_status.status == "pending":
                        task.status = "pending"
                    elif job_status.status == "running":
                        task.status = "running"
                    elif job_status.status == "completed":
                        task.status = "completed"
                        task.result_data = job_status.files
                        logger.info(f"Task {task_id} completed successfully")
                        session.commit()
                        break
                    elif job_status.status == "failed":
                        task.status = "failed"
                        task.error_message = job_status.error_message
                        logger.error(f"Task {task_id} failed: {job_status.error_message}")
                        session.commit()
                        break

                    session.commit()

                except Exception as e:
                    logger.error(f"Error polling analysis service: {e}", exc_info=True)
                    # Continue polling despite errors
                    pass

                # Wait before next poll
                time.sleep(poll_interval)

        except Exception as e:
            logger.error(f"Fatal error in polling task: {e}", exc_info=True)
            task = session.get(Task, task_id)
            if task:
                task.status = "failed"
                task.error_message = f"Polling error: {str(e)}"
                session.commit()

@router.get("/{task_id}", response_model=List[TaskPublic])
def read_reports(session: SessionDep, task_id: uuid.UUID) -> Any:
    """
    Retrieve report the report.
    """
    # TODO: restituzione report .md oppure formato bytes
    return NotImplementedError("Endpoint not yet implemented")

@router.get("/task_status/{task_id}", response_model=TaskPublic)
def read_task(session: SessionDep, task_id: uuid.UUID) -> Any:
    """
    Get task by ID.
    """
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # TODO: solo se la logica è da modificare per eseguire polling

    return task


@router.post("/company-info", response_model=TaskPublic)
def create_task(
    *,
    session: SessionDep,
    company_info: CompanyInfoCreate,
    background_tasks: BackgroundTasks
) -> Any:
    """Questa API riceve i dati in post della company info ed esegue:
    1. crea una nuova company info
    2. crea un nuovo task associato alla company info
    3. avvia il processo in background per la generazione del report

    Args:
        session (SessionDep): sessione del database
        company_info (CompanyInfoCreate): dati della company
        background_tasks (BackgroundTasks): task in background

    Returns:
        Any: il task creato
    """
    logger.info(f"Received request to analyze company: {company_info.name}")

    # 1. Crea una nuova company info
    company_info_create = CompanyInfo.model_validate(company_info)
    session.add(company_info_create)
    session.commit()
    session.refresh(company_info_create)

    logger.info(f"Company info created with ID: {company_info_create.id}")

    # 2. Crea un nuovo task associato alla company info
    task = Task(
        company_info_id=company_info_create.id,
        status="pending"  # TODO: definire gli status come Enum
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    logger.info(f"Task created with ID: {task.id}")

    # 3. Submit analysis job to analysis service
    try:
        client = AnalysisServiceClient()

        # Prepare company info for analysis service
        analysis_request = CompanyInfoRequest(
            name=company_info_create.name,
            url_linkedin=company_info_create.url_linkedin,
            url_sito=company_info_create.url_sito,
            nazione=company_info_create.nazione,
            citta=company_info_create.citta,
            settore=company_info_create.settore,
            tipo_azienda=company_info_create.tipo_azienda.value
        )

        # Submit job to analysis service
        analysis_job_id = client.create_analysis(analysis_request)

        logger.info(
            f"Analysis job submitted successfully. "
            f"Task ID: {task.id}, Analysis Job ID: {analysis_job_id}"
        )

        # Start background task to poll for status updates
        background_tasks.add_task(
            poll_analysis_service,
            task.id,
            analysis_job_id,
            session
        )

        logger.info(f"Background polling task started for task {task.id}")

    except Exception as e:
        logger.error(f"Error submitting analysis job: {e}", exc_info=True)

        # Update task status to failed
        task.status = "failed"
        task.error_message = f"Failed to submit analysis job: {str(e)}"
        session.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit analysis job: {str(e)}"
        )

    # TODO: al termine della generazione del report inviare per email il link al report
    # puoi usare questo codice come esempio:

    # report_link = f"https://example.com/reports/{task.id}"
    # email_data = background_tasks.add_task(
    #     generate_send_report_email,
    #     email_to=company_info_create.cta_email,
    #     report_link=report_link
    # )

    # send_email(
    #     email_to=company_info_create.cta_email,
    #     subject=email_data.subject,
    #     html_content=email_data.html_content,
    # )
    return TaskPublic.validate(task)
