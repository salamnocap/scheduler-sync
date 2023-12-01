from sqlalchemy import select, insert, update, delete

from app.database import get_all, get_one, execute_insert, execute_update, execute_delete
from app.opc_servers.models import OPCServer, PLCServer
from app.opc_servers.schemas import (OpcServerCreate, OpcServerUpdate, OpcServerSchema,
                                     PlcServerCreate, PlcServerUpdate, PlcServerSchema)


async def get_opc_servers() -> list[OpcServerSchema]:
    statement = select(OPCServer)
    opc_servers = await get_all(statement)
    return opc_servers


async def get_opc_server(id: str) -> OpcServerSchema | None:
    statement = select(OPCServer).where(OPCServer.id == id)
    opc_server = await get_one(statement)
    return opc_server


async def create_opc_server(data: OpcServerCreate) -> OpcServerSchema:
    statement = insert(OPCServer).values(data.model_dump()).returning(OPCServer)
    opc_server = await execute_insert(statement)
    return opc_server


async def update_opc_server(id: str, data: OpcServerUpdate) -> OpcServerSchema:
    statement = update(OPCServer).where(OPCServer.id == id).values(data.model_dump()).returning(OPCServer)
    opc_server = await execute_update(statement)
    return opc_server


async def delete_opc_server(id: str) -> None:
    statement = delete(OPCServer).where(OPCServer.id == id)
    await execute_delete(statement)


async def get_plc_servers() -> list[PlcServerSchema]:
    statement = select(PLCServer)
    plc_servers = await get_all(statement)
    return plc_servers


async def get_plc_server(id: str) -> PlcServerSchema | None:
    statement = select(PLCServer).where(PLCServer.id == id)
    plc_server = await get_one(statement)
    return plc_server


async def create_plc_server(data: PlcServerCreate) -> PlcServerSchema:
    statement = insert(PLCServer).values(data.model_dump()).returning(PLCServer)
    plc_server = await execute_insert(statement)
    return plc_server


async def update_plc_server(id: str, data: PlcServerUpdate) -> PlcServerSchema:
    statement = update(PLCServer).where(PLCServer.id == id).values(data.model_dump()).returning(PLCServer)
    plc_server = await execute_update(statement)
    return plc_server


async def delete_plc_server(id: str) -> None:
    statement = delete(PLCServer).where(PLCServer.id == id)
    await execute_delete(statement)
