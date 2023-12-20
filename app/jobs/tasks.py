from celery import shared_task, Celery

from app.jobs.mongo_crud import create_document, get_last_document
from app.jobs.schemas import DataSchema, DataSchemaWDiff
from app.opc_clients.service import get_value_from_opc, get_value_from_plc
from app.opc_clients.clients import OpcClient, Snap7Client
from app.config import settings


celery = Celery('tasks', broker=settings.broker_url)


@shared_task
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


@shared_task
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
