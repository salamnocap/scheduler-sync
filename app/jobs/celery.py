from celery import Celery
from app.config import settings

celery = Celery('celery', broker=settings.broker_url)


def schedule_task(task_name, schedule_time, task_args=(), task_kwargs=None):
    if task_kwargs is None:
        task_kwargs = {}

    celery.conf.beat_schedule[task_name] = {
        'task': task_name,
        'schedule': schedule_time,
        'args': task_args,
        'kwargs': task_kwargs,
    }

# Call the function with the task name, the schedule time and the task parameters
schedule_task("app.jobs.tasks.save_value_from_opc", crontab(minute='*/1'),
              task_args=('collection_name', 'opc_ip', 1234, 'node_id', True))  # runs every minute
