"""
Worker main entry point
"""

import asyncio
import logging
import os
from celery import Celery

from app.core.config import settings
from app.db.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "ecdat_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.SCAN_TIMEOUT_SECONDS,
    worker_prefetch_multiplier=1,
)

# Import tasks to register them
from app.tasks import scan_tasks

if __name__ == "__main__":
    celery_app.start()