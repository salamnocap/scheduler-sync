from celery import Celery
from app.config import settings

celery = Celery('celery', broker=settings.broker_url)
