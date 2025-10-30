from fastapi import APIRouter, HTTPException
import uuid
from typing import Any, List
import logging

from app.api.deps import SessionDep
from app.services import get_analysis_service
from app.models import CompanyInfo, TaskPublic, CompanyInfoCreate, Task
# from utils.email import generate_send_report_email, send_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/report", tags=["report"])

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
    company_info: CompanyInfoCreate
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
        service = get_analysis_service()

        # Prepare company info for analysis service
        analysis_company_info = CompanyInfo(
            name=company_info_create.name,
            url_linkedin=company_info_create.url_linkedin,
            url_sito=company_info_create.url_sito,
            nazione=company_info_create.nazione,
            citta=company_info_create.citta,
            settore=company_info_create.settore,
            tipo_azienda=company_info_create.tipo_azienda
        )

        # Submit job to analysis service with task_id for database updates
        # The service will update the task status directly in the database
        analysis_job_id = service.create_job(
            company_info=analysis_company_info,
            task_id=str(task.id)
        )

        logger.info(
            f"Analysis job submitted successfully. "
            f"Task ID: {task.id}, Analysis Job ID: {analysis_job_id}. "
            f"Status will be updated automatically in database."
        )

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
