from celery import Celery
from celery.schedules import crontab

from app.config import settings


celery = Celery('tasks', settings.broker_url)


def create_cron_task(name: str, cron: dict, func, args: list[str] | None = None):
    celery.conf.beat_schedule[name] = {
        'task': func,
        'schedule': crontab(minute=cron['minute'], hour=cron['hour'], day_of_week=cron['day_of_week']),
        'args': args
    }


def create_periodic_task(name: str, seconds: int, func, args: list[str] | None = None):
    celery.conf.beat_schedule[name] = {
        'task': func,
        'schedule': seconds,
        'args': args
    }


def delete_task(name: str):
    del celery.conf.beat_schedule[name]
