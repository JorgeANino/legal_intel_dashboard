"""
Celery tasks
"""
from app.core.celery_app import celery_app


from app.tasks.document_tasks import *
