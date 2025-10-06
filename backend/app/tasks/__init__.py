"""
Celery tasks
"""
# Local application imports
from app.core.celery_app import celery_app
from app.tasks.document_tasks import process_document_task

__all__ = ["celery_app", "process_document_task"]
