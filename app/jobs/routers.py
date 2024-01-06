from fastapi import APIRouter, HTTPException

from app.jobs.schemas import JobSchema, JobCreate
from app.jobs import service
from app.opc_servers.service import check_opc_server_by_id, check_plc_server_by_id
from app.jobs.scheduler import scheduler, add_job_if_applicable, delete_job_if_applicable
from app.config import settings
from app.jobs.mongo_crud import (create_collection, delete_collection, get_collection, get_db_collections)


router = APIRouter()


@router.get("/", response_model=list[JobSchema])
async def get_jobs():
    return await service.get_jobs()


@router.get("/scheduled", response_model=list[dict])
async def get_scheduled_jobs():
    jobs = await service.get_jobs()
    scheduled_jobs = set(
        scheduled_job['_id'] for scheduled_job in get_collection(
            db_name=settings.mongodb_jobstore,
            collection_name=settings.mongodb_jobstore_collection
        )
    )

    response = []

    for job in jobs:
        scheduled = job.id in scheduled_jobs
        response.append({
            "id": job.id,
            "job": job,
            "scheduled": scheduled
        })

    return response


@router.get("/{id}",
            response_model=JobSchema)
async def get_job_by_id(id: int):
    job = await service.get_job(id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.get("/name/{name}",
            response_model=JobSchema)
async def get_job_by_name(name: str):
    job = await service.get_job_by_name(name)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.post("/", status_code=201)
async def create_job(job: JobCreate, diff_field: bool = False):

    if job.opc_id:
        await check_opc_server_by_id(job.opc_id)
    if job.plc_id:
        await check_plc_server_by_id(job.plc_id)

    job_creds = await service.create_job(job)
    create_collection(db_name=settings.mongodb_db, collection_name=job_creds.name)

    args = await service.get_schedule_args(job, job_creds, diff_field)
    job_id = str(job_creds.id)
    add_job_if_applicable(job, job_id, scheduler, args)

    return job_creds


@router.delete("/{id}",
               status_code=204,
               response_model=None)
async def delete_job(id: int):
    job = await service.get_job(id)
    delete_job_if_applicable(id, scheduler)
    delete_collection(db_name=settings.mongodb_db, collection_name=job.name)
    await service.delete_job(id)


@router.delete("/name/{name}",
               status_code=204,
               response_model=None)
async def delete_job_by_name(name: str):
    job = await service.get_job_by_name(name)
    delete_job_if_applicable(job.id, scheduler)
    delete_collection(db_name=settings.mongodb_db, collection_name=job.name)
    await service.delete_job(job.id)


@router.get("/collection/{collection_name}",
            response_model=list[dict])
async def get_collection_by_jobname(collection_name: str,
                                    sort_by: str = None,
                                    sort_order: int = -1,
                                    limit: int = 100,
                                    skip: int = 0):
    db_collections = get_db_collections(db_name=settings.mongodb_db)

    if collection_name not in db_collections:
        raise HTTPException(status_code=404, detail="Collection not found")

    collection_data = get_collection(
        db_name=settings.mongodb_db,
        collection_name=collection_name,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        skip=skip
    )

    return {
        "collection_name": collection_name,
        "collection_data": collection_data,
        "db_collections": db_collections
    }


@router.get("/collection",
            response_model=list[dict])
def get_collections():
    return get_db_collections(db_name=settings.mongodb_db)
