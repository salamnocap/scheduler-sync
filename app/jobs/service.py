from sqlalchemy import select, insert, delete
from datetime import datetime

from app.database import get_all, get_one, execute_insert, execute_delete
from app.jobs.models import Job
from app.jobs.schemas import JobCreate, JobSchema
from app.opc_servers.service import get_opc_server, get_plc_server
from app.jobs.mongo_crud import create_document, get_last_document
from app.jobs.schemas import DataSchema, DataSchemaWDiff
from app.opc_clients.service import get_value_from_opc, get_value_from_plc
from app.opc_clients.clients import OpcClient, Snap7Client
from app.config import settings


async def get_jobs() -> list[JobSchema]:
    statement = select(Job)
    jobs = await get_all(statement)
    return jobs


async def get_job(id: int) -> JobSchema | None:
    statement = select(Job).where(Job.id == id)
    job = await get_one(statement)
    return job


async def get_job_by_name(name: str) -> JobSchema | None:
    statement = select(Job).where(Job.name == name)
    job = await get_one(statement)
    return job


async def create_job(data: JobCreate) -> JobSchema:
    statement = insert(Job).values(data.model_dump()).returning(Job)
    job = await execute_insert(statement)
    return job


async def delete_job(id: int) -> None:
    statement = delete(Job).where(Job.id == id)
    await execute_delete(statement)


async def get_schedule_args(job, job_creds, diff_field):
    if job.opc_id:
        opc = await get_opc_server(id=job.opc_id)
        variable_part = f'."{opc.node_id["variable"]}"' if opc.node_id["variable"] else ''
        node_id = f'ns={opc.node_id["namespace"]};s="{opc.node_id["server"]}"{variable_part}'
        args = {
            'collection_name': job_creds.name,
            'opc_ip': opc.ip_address,
            'port': opc.port,
            'node_id': node_id,
            'diff_field': diff_field
        }
    else:
        plc = await get_plc_server(id=job.plc_id)
        args = {
            'collection_name': job_creds.name,
            'plc_ip': plc.ip_address,
            'rack': plc.rack,
            'slot': plc.slot,
            'db': plc.db,
            'offset': plc.offset,
            'size': plc.size,
            'diff_field': diff_field
        }

    return args


def save_value_from_opc(collection_name: str, opc_ip: str, port: int,
                        node_id: str, diff_field: bool) -> None:
    opc_client = OpcClient(opc_ip, port)
    value = get_value_from_opc(opc_client, node_id)
    last_doc = get_last_document(db_name=settings.mongodb_db, collection_name=collection_name)

    if last_doc:
        last_value = last_doc.get('value', 0.0)
        diff = max(0.0, value - last_value)
    else:
        diff = 0.0

    datetime_now = datetime.now()

    if diff_field and diff > 0.0:
        data = DataSchemaWDiff(datetime=datetime_now, value=value, difference=diff)
        create_document(db_name=settings.mongodb_db, collection_name=collection_name, document=data.to_dict())
    elif not diff_field:
        data = DataSchema(datetime=datetime_now, value=value)
        create_document(db_name=settings.mongodb_db, collection_name=collection_name, document=data.to_dict())


def save_value_from_plc(collection_name: str, plc_ip: str, rack: int, slot: int,
                        db: int, offset: int, size: int, diff_field: bool) -> None:
    plc_client = Snap7Client(plc_ip, rack, slot)
    value = get_value_from_plc(plc_client, db, offset, size)
    last_doc = get_last_document(db_name=settings.mongodb_db, collection_name=collection_name)

    if last_doc:
        last_value = last_doc.get('value', 0.0)
        diff = max(0.0, value - last_value)
    else:
        diff = 0.0

    datetime_now = datetime.now()

    if diff_field and diff > 0.0:
        data = DataSchemaWDiff(datetime=datetime_now, value=value, difference=diff)
        create_document(db_name=settings.mongodb_db, collection_name=collection_name, document=data.to_dict())
    elif not diff_field:
        data = DataSchema(datetime=datetime_now, value=value)
        create_document(db_name=settings.mongodb_db, collection_name=collection_name, document=data.to_dict())
