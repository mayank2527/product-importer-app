import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DEBUG = True


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")


config_settings = {"development": DevelopmentConfig}
