from pytz import utc

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.executors.pool import ProcessPoolExecutor

from app.config import settings
from app.database import mongo_client
from app.jobs.service import save_value_from_plc, save_value_from_opc


scheduler = BackgroundScheduler(
    jobstores={
        'default': MongoDBJobStore(database=settings.mongodb_jobstore,
                                   collection=settings.mongodb_jobstore_collection,
                                   client=mongo_client)
    },
    executors={
        'default': {'type': 'threadpool', 'max_workers': settings.scheduler_max_workers},
        'processpool': ProcessPoolExecutor(max_workers=settings.scheduler_max_workers)
    },
    job_defaults={
        'coalesce': settings.scheduler_coalesce,
        'max_instances': settings.scheduler_max_instances
    }
)


def add_job_if_applicable(job, job_id, scheduler_type: BackgroundScheduler, args):
    if job.details.job_type == 'cron':
        details = job.details.cron_task
        scheduler_type.add_job(execute_job,
                               CronTrigger(
                                   day_of_week=details.day_of_week,
                                   hour=details.hour,
                                   minute=details.minute,
                                   timezone=utc
                               ),
                               args=[args],
                               id=job_id,
                               name=job.name)
    if job.details.job_type == 'periodic':
        details = job.details.periodic_task
        scheduler_type.add_job(execute_job,
                               CronTrigger(
                                   minute=details.interval,
                                   timezone=utc
                               ),
                               args=[args],
                               id=job_id,
                               name=job.name)


def delete_job_if_applicable(job_id: int, scheduler_type: BackgroundScheduler):
    job_id = str(job_id)
    scheduler_type.remove_job(job_id)


def execute_job(job_args):
    if job_args["opc_ip"]:
        save_value_from_opc(job_args['collection_name'], job_args['opc_ip'], job_args['port'],
                            job_args['node_id'], job_args['diff_field'])
    else:
        save_value_from_plc(job_args['collection_name'], job_args['plc_ip'], job_args['rack'], job_args['slot'],
                            job_args['db'], job_args['offset'], job_args['size'], job_args['diff_field'])
