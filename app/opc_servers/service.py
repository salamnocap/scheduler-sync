from fastapi import HTTPException
from sqlalchemy import select, insert, update, delete
from uuid import UUID

from app.database import get_all, get_one, execute_insert, execute_update, execute_delete
from app.opc_servers.models import OPCServer, PLCServer
from app.opc_servers.schemas import (OpcServerCreate, OpcServerUpdate, OpcServerSchema,
                                     PlcServerCreate, PlcServerUpdate, PlcServerSchema, OpcNodeID)
from app.opc_clients.service import get_value_from_opc, get_value_from_plc
from app.opc_clients.clients import OpcClient, Snap7Client


def check_opc_server(data: OpcServerCreate) -> bool:
    opc_client = OpcClient(data.ip_address, data.port)
    get_value_from_opc(opc_client, data.node_id.to_string())
    return True


async def get_opc_servers() -> list[OpcServerSchema]:
    statement = select(OPCServer)
    opc_servers = await get_all(statement)
    return opc_servers


async def get_opc_server(id: UUID) -> OpcServerSchema | None:
    statement = select(OPCServer).where(OPCServer.id == id)
    opc_server = await get_one(statement)
    return opc_server


async def create_opc_server(data: OpcServerCreate) -> OpcServerSchema:
    if not check_opc_server(data):
        raise HTTPException(status_code=500, detail="Cannot connect to OPC Server")
    statement = insert(OPCServer).values(data.model_dump()).returning(OPCServer)
    opc_server = await execute_insert(statement)
    return opc_server


async def update_opc_server(id: UUID, data: OpcServerUpdate) -> OpcServerSchema:
    values = data.model_dump(exclude_none=True)
    statement = update(OPCServer).where(OPCServer.id == id).values(values).returning(OPCServer)
    opc_server = await execute_update(statement)
    return opc_server


async def delete_opc_server(id: UUID) -> None:
    statement = delete(OPCServer).where(OPCServer.id == id)
    await execute_delete(statement)


def check_plc_server(data: PlcServerCreate) -> bool:
    plc_client = Snap7Client(data.ip_address, data.rack, data.slot)
    get_value_from_plc(plc_client, data.db, data.offset, data.size)
    return True


async def get_plc_servers() -> list[PlcServerSchema]:
    statement = select(PLCServer)
    plc_servers = await get_all(statement)
    return plc_servers


async def get_plc_server(id: UUID) -> PlcServerSchema | None:
    statement = select(PLCServer).where(PLCServer.id == id)
    plc_server = await get_one(statement)
    return plc_server


async def create_plc_server(data: PlcServerCreate) -> PlcServerSchema:
    if not check_plc_server(data):
        raise HTTPException(status_code=500, detail="Cannot connect to PLC Server")
    statement = insert(PLCServer).values(data.model_dump()).returning(PLCServer)
    plc_server = await execute_insert(statement)
    return plc_server


async def update_plc_server(id: UUID, data: PlcServerUpdate) -> PlcServerSchema:
    values = data.model_dump(exclude_none=True)
    statement = update(PLCServer).where(PLCServer.id == id).values(values).returning(PLCServer)
    plc_server = await execute_update(statement)
    return plc_server


async def delete_plc_server(id: UUID) -> None:
    statement = delete(PLCServer).where(PLCServer.id == id)
    await execute_delete(statement)


async def check_opc_server_by_id(id: UUID) -> bool:
    opc = await get_opc_server(id)
    if not opc:
        raise HTTPException(status_code=404, detail="OPC Server not found")
    if not opc.enabled:
        raise HTTPException(status_code=500, detail="OPC Server is not enabled")

    opc_client = OpcClient(opc.ip_address, opc.port)
    variable_part = f'."{opc.node_id.variable}"' if opc.node_id.variable is not None else ''
    node_id = f'ns={opc.node_id.namespace};s="{opc.node_id.server}"{variable_part}'
    get_value_from_opc(opc_client, node_id)
    return True


async def check_plc_server_by_id(id: UUID) -> bool:
    plc = await get_plc_server(id)
    if not plc:
        raise HTTPException(status_code=404, detail="PLC Server not found")
    if not plc.enabled:
        raise HTTPException(status_code=500, detail="PLC Server is not enabled")

    plc_client = Snap7Client(plc.ip_address, plc.rack, plc.slot)
    get_value_from_plc(plc_client, plc.db, plc.offset, plc.size)
    return True
