from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.opc_servers.routers import router as opc_server_router
from app.jobs.routers import router as job_router


app = FastAPI(title="OPC-PRO-SCHEDULER", docs_url="/auth/docs", openapi_url="/auth/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(opc_server_router, prefix="/api/servers", tags=["servers"])
app.include_router(job_router, prefix="/api/jobs", tags=["jobs"])
