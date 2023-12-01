from fastapi import APIRouter, HTTPException

from app.opc_servers.schemas import (OpcServerSchema, OpcServerCreate, OpcServerUpdate,
                                     PlcServerCreate, PlcServerUpdate, PlcServerSchema)
from app.opc_servers import service


router = APIRouter()


@router.get("/opc_servers",
            response_model=list[OpcServerSchema])
async def get_opc_servers():
    return await service.get_opc_servers()


@router.get("/opc_servers/{id}",
            response_model=OpcServerSchema)
async def get_opc_server(id: str):
    opc_server = await service.get_opc_server(id)
    if not opc_server:
        raise HTTPException(status_code=404, detail="Opc Server not found")
    print(opc_server.id, opc_server.name)

    return opc_server


@router.post("/opc_servers",
             status_code=201,
             response_model=OpcServerSchema)
async def create_opc_server(opc_server: OpcServerCreate):
    return await service.create_opc_server(opc_server)


@router.patch("/opc_servers/{id}",
              response_model=OpcServerSchema)
async def update_opc_server(id: str, opc_server: OpcServerUpdate):
    return await service.update_opc_server(id, opc_server)


@router.delete("/opc_servers/{id}",
               status_code=204,
               response_model=None)
async def delete_opc_server(id: str):
    await service.delete_opc_server(id)


@router.get("/plc_servers",
            response_model=list[PlcServerSchema])
async def get_plc_servers():
    return await service.get_plc_servers()


@router.get("/plc_servers/{id}",
            response_model=PlcServerSchema)
async def get_plc_server(id: str):
    print(id)
    plc_server = await service.get_plc_server(id)
    if not plc_server:
        raise HTTPException(status_code=404, detail="Plc Server not found")
    print(plc_server.id, plc_server.name)

    return plc_server


@router.post("/plc_servers",
             status_code=201,
             response_model=PlcServerSchema)
async def create_plc_server(plc_server: PlcServerCreate):
    return await service.create_plc_server(plc_server)


@router.patch("/plc_servers/{id}",
              response_model=PlcServerSchema)
async def update_plc_server(id: str, plc_server: PlcServerUpdate):
    return await service.update_plc_server(id, plc_server)


@router.delete("/plc_servers/{id}",
                status_code=204,
                response_model=None)
async def delete_plc_server(id: str):
    await service.delete_plc_server(id)
