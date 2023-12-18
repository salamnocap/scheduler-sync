from fastapi import APIRouter, HTTPException

from app.jobs.schemas import JobSchema, JobCreate
from app.jobs import service
from app.jobs.mongo_crud import create_collection, delete_collection, get_collection
from app.jobs.service import save_value_from_opc, save_value_from_plc
from app.opc_servers.service import check_opc_server_by_id, check_plc_server_by_id, get_opc_server, get_plc_server
from app.opc_servers.schemas import OpcServerSchema, PlcServerSchema
from app.jobs.tasks import create_cron_task, create_periodic_task, delete_task


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
    opc_bool = False

    if job.opc_id:
        await check_opc_server_by_id(job.opc_id)
        opc_bool = True
    if job.plc_id:
        await check_plc_server_by_id(job.plc_id)

    job_creds = await service.create_job(job)
    create_collection(collection_name=job_creds.name)

    if opc_bool:
        opc = await get_opc_server(id=job.opc_id)
        opc = OpcServerSchema.validate_model(opc)
        args = [job_creds.name, opc.ip_address, opc.port, opc.node_id.to_string(), diff_field]
        function = save_value_from_opc
    else:
        plc = await get_plc_server(id=job.plc_id)
        plc = PlcServerSchema.validate_model(plc)
        args = [job_creds.name, plc.ip_address, plc.rack, plc.slot, plc.db, plc.offset, plc.size, diff_field]
        function = save_value_from_plc

    if job.details.job_type == "cron":
        create_cron_task(name=job.name,
                         cron=job.details['cron_task'],
                         func=function,
                         args=args)
    elif job.details.job_type == "periodic":
        create_periodic_task(name=job.name,
                             seconds=job.details.periodic_task.interval,
                             func=function,
                             args=args)

    return job_creds


@router.delete("/{id}",
               status_code=204,
               response_model=None)
async def delete_job(id: int):
    job = await service.get_job(id)
    delete_task(job.name)
    delete_collection(job.name)
    await service.delete_job(id)


@router.get("/collection/{collection_name}",
            response_model=list[dict])
async def get_collection_by_name(collection_name: str,
                                 sort_by: str = None,
                                 sort_order: int = -1,
                                 limit: int = 100,
                                 skip: int = 0):
    return get_collection(collection_name, sort_by, sort_order, limit, skip)
