from sqlalchemy import select, insert, delete

from app.database import get_all, get_one, execute_insert, execute_delete
from app.jobs.models import Job
from app.jobs.schemas import JobCreate, JobSchema
from app.opc_servers.service import get_opc_server, get_plc_server


async def get_jobs() -> list[JobSchema]:
    statement = select(Job)
    jobs = await get_all(statement)
    return jobs


async def get_job(id: int) -> JobSchema | None:
    statement = select(Job).where(Job.id == id)
    job = await get_one(statement)
    return job


async def create_job(data: JobCreate) -> JobSchema:
    statement = insert(Job).values(data.model_dump()).returning(Job)
    job = await execute_insert(statement)
    return job


async def delete_job(id: int) -> None:
    statement = delete(Job).where(Job.id == id)
    await execute_delete(statement)


async def get_schedule_args_function(job, job_creds, diff_field):
    if job.opc_id:
        opc = await get_opc_server(id=job.opc_id)
        variable_part = f'."{opc.node_id["variable"]}"' if opc.node_id["variable"] else ''
        node_id = f'ns={opc.node_id["namespace"]};s="{opc.node_id["server"]}"{variable_part}'
        args = [job_creds.name, opc.ip_address, opc.port, node_id, diff_field]
        function = 'save_value_from_opc'
    else:
        plc = await get_plc_server(id=job.plc_id)
        args = [job_creds.name, plc.ip_address, plc.rack, plc.slot, plc.db, plc.offset, plc.size, diff_field]
        function = 'save_value_from_plc'

    return args, function
