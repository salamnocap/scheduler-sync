from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.opc_servers.opc_routers import router as opc_server_router
from app.opc_servers.plc_routers import router as plc_server_router
from app.jobs.routers import router as job_router


app = FastAPI(title="OPC-PRO-SCHEDULER", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(opc_server_router, prefix="/api", tags=["OPC Servers"])
app.include_router(plc_server_router, prefix="/api", tags=["PLC Servers"])
app.include_router(job_router, prefix="/api/jobs", tags=["jobs"])
