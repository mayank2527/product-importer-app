from celery import Celery

from app.config import config_settings

# Initialize Celery
celery = Celery(
    "worker",
    broker=config_settings["celery_config"].CELERY_BROKER_URL,
    backend=config_settings["celery_config"].CELERY_RESULT_BACKEND,
)
