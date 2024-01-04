from sqlalchemy import select, insert, delete
import logging
from datetime import datetime

from app.database import get_all, get_one, execute_insert, execute_delete
from app.jobs.models import Job
from app.jobs.schemas import JobCreate, JobSchema
from app.opc_servers.service import get_opc_server, get_plc_server
from app.jobs.mongo_crud import create_document, get_last_document
from app.jobs.schemas import DataSchema, DataSchemaWDiff
from app.opc_clients.service import get_value_from_opc, get_value_from_plc
from app.opc_clients.clients import OpcClient, Snap7Client


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
                        node_id: str, diff_field: bool = False) -> None:
    opc_client = OpcClient(opc_ip, port)
    value = get_value_from_opc(opc_client, node_id)

    logging.info(f'Retrieved value from OPC: {value}')

    data = DataSchema(value=value)

    if diff_field:
        last_doc = get_last_document(collection_name)
        if not last_doc:
            data = DataSchemaWDiff(value=value, diff=0)
        else:
            last_value = last_doc['value']
            diff = value - last_value
            data = DataSchemaWDiff(value=value, diff=diff)

    logging.info(f'Prepared data for saving: {data.to_dict()}')

    create_document(collection_name, data.to_dict())

    logging.info('Finished save_value_from_opc task')
    logging.info(datetime.utcnow())


def save_value_from_plc(collection_name: str, plc_ip: str, rack: int, slot: int,
                        db: int, offset: int, size: int, diff_field: bool = False) -> None:
    plc_client = Snap7Client(plc_ip, rack, slot)
    value = get_value_from_plc(plc_client, db, offset, size)

    logging.info(f'Retrieved value from PLC: {value}')

    data = DataSchema(value=value)

    if diff_field:
        last_doc = get_last_document(collection_name)
        if not last_doc:
            data = DataSchemaWDiff(value=value, diff=0)
        else:
            last_value = last_doc['value']
            diff = value - last_value
            data = DataSchemaWDiff(value=value, diff=diff)

    logging.info(f'Prepared data for saving: {data.to_dict()}')

    create_document(collection_name, data.to_dict())

    logging.info('Finished save_value_from_plc task')
    logging.info(datetime.utcnow())
