from fastapi import APIRouter, HTTPException
from uuid import UUID

from app.opc_servers.schemas import PlcServerCreate, PlcServerUpdate, PlcServerSchema
from app.opc_servers import service


router = APIRouter()


@router.get("/plc_servers",
            response_model=list[PlcServerSchema])
async def get_plc_servers():
    return await service.get_plc_servers()


@router.get("/plc_servers/{id}",
            response_model=PlcServerSchema)
async def get_plc_server(id: UUID):
    plc_server = await service.get_plc_server(id)
    if not plc_server:
        raise HTTPException(status_code=404, detail="Plc Server not found")

    return plc_server


@router.post("/plc_servers",
             status_code=201,
             response_model=PlcServerSchema)
async def create_plc_server(plc_server: PlcServerCreate):
    return await service.create_plc_server(plc_server)


@router.patch("/plc_servers/{id}",
              response_model=PlcServerSchema)
async def update_plc_server(id: UUID, plc_server: PlcServerUpdate):
    return await service.update_plc_server(id, plc_server)


@router.delete("/plc_servers/{id}",
               status_code=204,
               response_model=None)
async def delete_plc_server(id: UUID):
    await service.delete_plc_server(id)
