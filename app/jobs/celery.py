from celery import Celery
from app.config import settings

celery = Celery('tasks', broker=settings.broker_url)
