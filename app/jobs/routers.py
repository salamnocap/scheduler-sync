from fastapi import APIRouter, HTTPException

from app.jobs.schemas import JobSchema, JobCreate
from app.jobs import service
from app.jobs.mongo_crud import create_collection, delete_collection, get_collection, get_collections
from app.opc_servers.service import check_opc_server_by_id, check_plc_server_by_id
from app.jobs.scheduler import add_job_if_applicable, scheduler, delete_job_if_applicable


router = APIRouter()


@router.get("/",
            response_model=list[JobSchema])
async def get_jobs():
    return await service.get_jobs()


@router.get("/{id}",
            response_model=JobSchema)
async def get_job(id: int):
    job = await service.get_job(id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    print(job.id, job.name)

    return job


@router.post("/", status_code=201)
async def create_job(job: JobCreate, diff_field: bool = False):

    if job.opc_id:
        await check_opc_server_by_id(job.opc_id)
    if job.plc_id:
        await check_plc_server_by_id(job.plc_id)

    job_creds = await service.create_job(job)
    create_collection(collection_name=job_creds.name)

    args = await service.get_schedule_args(job, job_creds, diff_field)

    job["args"] = args

    add_job_if_applicable(job, scheduler)

    return job_creds


@router.delete("/{id}",
               status_code=204,
               response_model=None)
async def delete_job(id: int):
    job = await service.get_job(id)
    delete_collection(job.name)
    await service.delete_job(id)
    delete_job_if_applicable(id, scheduler)


@router.get("/collection/{collection_name}",
            response_model=list[dict])
async def get_collection_by_name(collection_name: str,
                                 sort_by: str = None,
                                 sort_order: int = -1,
                                 limit: int = 100,
                                 skip: int = 0):
    return get_collection(collection_name, sort_by, sort_order, limit, skip)


@router.get("/collection",
            response_model=list[dict])
def get_collections():
    return get_collections()
