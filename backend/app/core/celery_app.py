"""
Production Celery configuration with retry logic
"""
# Local application imports
# Third-party imports
from celery import Celery

from app.core.config import settings


# Create Celery instance
celery_app = Celery(
    "legal_intel",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.document_tasks"],
)

# Production-grade Celery config
celery_app.conf.update(
    # Task execution
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Performance
    task_acks_late=True,  # Acknowledge after completion
    worker_prefetch_multiplier=1,  # Process one task at a time
    # Reliability
    task_reject_on_worker_lost=True,
    task_track_started=True,
    # Retry policy
    task_default_retry_delay=30,  # 30 seconds
    task_max_retries=3,
    # Time limits
    task_soft_time_limit=300,  # 5 minutes soft limit
    task_time_limit=600,  # 10 minutes hard limit
    # Result backend
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={"master_name": "mymaster"},
)

# Configure task routes (use default 'celery' queue)
celery_app.conf.task_routes = {
    "app.tasks.*": {"queue": "celery"},
}
