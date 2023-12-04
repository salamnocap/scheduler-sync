from fastapi import APIRouter, HTTPException
from uuid import UUID

from app.opc_servers.schemas import OpcServerSchema, OpcServerCreate, OpcServerUpdate
from app.opc_servers import service


router = APIRouter()


@router.get("/opc_servers",
            response_model=list[OpcServerSchema])
async def get_opc_servers():
    return await service.get_opc_servers()


@router.get("/opc_servers/{id}",
            response_model=OpcServerSchema)
async def get_opc_server(id: UUID):
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
async def update_opc_server(id: UUID, opc_server: OpcServerUpdate):
    return await service.update_opc_server(id, opc_server)


@router.delete("/opc_servers/{id}",
               status_code=204,
               response_model=None)
async def delete_opc_server(id: UUID):
    await service.delete_opc_server(id)
