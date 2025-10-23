from fastapi import APIRouter, BackgroundTasks
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.models import CompanyInfo, TaskPublic, CompanyInfoCreate, Task
# from utils.email import generate_send_report_email, send_email
from typing import List

router = APIRouter(prefix="/report", tags=["report"])

@router.get("/{task_id}", response_model=List[TaskPublic])
def read_reports(session: SessionDep) -> Any:
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
    # 1. Crea una nuova company info
    company_info_create = CompanyInfo.model_validate(company_info)
    session.add(company_info_create)
    session.commit()
    session.refresh(company_info_create)

    # 2. Crea un nuovo task associato alla company info
    task = Task(
        company_info_id=company_info_create.id,
        status="pending" #TODO: definire gli status come Enum
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # 3. TODO: avvia il processo in background per la generazione del report
    # Esempio: background_tasks.add_task(generate_report, task.id)
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
    return task