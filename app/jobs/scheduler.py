import logging
from pytz import utc
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.executors.pool import ProcessPoolExecutor

from app.config import settings
from app.jobs.mongo_crud import get_collection
from app.database import mongo_client
from app.jobs.service import save_value_from_plc, save_value_from_opc


db = mongo_client[settings.mongodb_db]
scheduled_jobs_collection = db['scheduled_jobs']


scheduler = BackgroundScheduler(
    jobstores={
        'default': MongoDBJobStore(database='scheduler', collection='jobs', client=mongo_client)
    },
    executors={
        'default': {'type': 'threadpool', 'max_workers': 30},
        'processpool': ProcessPoolExecutor(max_workers=30)
    },
    job_defaults={
        'coalesce': False,
        'max_instances': 3
    }
)


scheduled_jobs_map = {}


def schedule_jobs():
    jobs = get_collection('scheduled_jobs')
    for job in jobs:
        add_job_if_applicable(job, scheduler)

    logging.info("Refreshed scheduled jobs")


def add_job_if_applicable(job, scheduler_type: BackgroundScheduler):
    job_id = str(job["id"])

    if job_id not in scheduled_jobs_map:
        scheduled_jobs_map[job_id] = job
        if job["details"]["job_type"] == 'cron':
            details = job["details"]["cron_task"]
            job_args = job["args"]
            scheduler_type.add_job(execute_job,
                                   CronTrigger(
                                       day_of_week=details['day_of_week'],
                                       hour=details['hour'],
                                       minute=details['minute'],
                                       timezone=utc
                                   ),
                                   args=[job_args],
                                   id=job_id,
                                   name=job["name"])
        if job["details"]["job_type"] == 'periodic':
            details = job["details"]["periodic_task"]
            job_args = job["args"]
            scheduler_type.add_job(execute_job,
                                   CronTrigger(
                                       second=details['interval'],
                                       timezone=utc
                                   ),
                                   args=[job_args],
                                   id=job_id,
                                   name=job["name"])

        logging.info("Added job with id: %s", job_id, " and name: ", job.name)


def delete_job_if_applicable(job_id: int, scheduler_type: BackgroundScheduler):
    job_id = str(job_id)

    if job_id in scheduled_jobs_map:
        scheduler_type.remove_job(job_id)
        del scheduled_jobs_map[job_id]
        logging.info("Deleted job with id: %s", job_id)


def execute_job(job_args):
    if job_args["opc_id"]:
        save_value_from_opc(job_args['collection_name'], job_args['opc_ip'], job_args['port'],
                            job_args['node_id'], job_args['diff_field'])
    else:
        save_value_from_plc(job_args['collection_name'], job_args['plc_ip'], job_args['rack'], job_args['slot'],
                            job_args['db'], job_args['offset'], job_args['size'], job_args['diff_field'])


scheduler.add_job(schedule_jobs, 'interval',
                  seconds=5, next_run_time=datetime.utcnow(),
                  id='scheduler-job-id')
