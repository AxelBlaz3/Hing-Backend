from datetime import timedelta
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

os.fspath(Path(__file__).parent.joinpath('uploads'))

class Config:
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=1440)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=365)
    MONGO_URI = os.environ.get('DEV_MONGO_URI')
    UPLOAD_FOLDER = 'static/uploads'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_USE_SSL = True


class ProductionConfig(Config):
    DEBUG = False
    MONGO_URI = os.environ.get('PROD_MONGO_URI')


class StagingConfig(Config):
    DEBUG = False
    MONGO_URI = os.environ.get('STAGING_MONGO_URI')
