from sqlalchemy import select, insert, delete

from app.database import get_all, get_one, execute_insert, execute_delete
from app.jobs.models import Job
from app.jobs.schemas import JobCreate, JobSchema, DataSchema, DataSchemaWDiff
from app.jobs.mongo_crud import create_document, get_last_document
from app.opc_clients.service import get_value_from_opc, get_value_from_plc
from app.opc_clients.clients import OpcClient, Snap7Client
from app.jobs.tasks import celery


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


@celery.task
def save_value_from_opc(collection_name: str, opc_ip: str, port: int,
                        node_id: str, diff_field: bool = False) -> None:
    opc_client = OpcClient(opc_ip, port)
    value = get_value_from_opc(opc_client, node_id)

    data = DataSchema(value=value)

    if diff_field:
        last_doc = get_last_document(collection_name)
        if not last_doc:
            data = DataSchemaWDiff(value=value, diff=0)
        else:
            last_value = last_doc['value']
            diff = value - last_value
            data = DataSchemaWDiff(value=value, diff=diff)

    create_document(collection_name, data.to_dict())


@celery.task
def save_value_from_plc(collection_name: str, plc_ip: str, rack: int, slot: int,
                        db: int, offset: int, size: int, diff_field: bool = False) -> None:
    plc_client = Snap7Client(plc_ip, rack, slot)
    value = get_value_from_plc(plc_client, db, offset, size)

    data = DataSchema(value=value)

    if diff_field:
        last_doc = get_last_document(collection_name)
        if not last_doc:
            data = DataSchemaWDiff(value=value, diff=0)
        else:
            last_value = last_doc['value']
            diff = value - last_value
            data = DataSchemaWDiff(value=value, diff=diff)

    create_document(collection_name, data.to_dict())
