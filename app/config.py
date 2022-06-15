import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DEBUG = True


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    BASE_URL = os.environ.get("BASE_URL")


class CeleryConfig:
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")


class FileUploadConfig:
    FILE_UPLOAD_PATH = os.environ.get("FILE_UPLOAD_PATH")


config_settings = {
    "development": DevelopmentConfig,
    "celery_config": CeleryConfig,
    "file_upload_config": FileUploadConfig,
}
