from fastapi import APIRouter, HTTPException

from app.jobs.schemas import JobSchema, JobCreate
from app.jobs import service


router = APIRouter()


@router.get("/",
            response_model=list[JobSchema])
async def get_jobs():
    return await service.get_jobs()


@router.get("/{id}",
            response_model=JobSchema)
async def get_job(id: str):
    job = await service.get_job(id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    print(job.id, job.name)

    return job


@router.post("/",
             status_code=201,
             response_model=JobSchema)
async def create_job(job: JobCreate):
    return await service.create_job(job)


@router.delete("/{id}",
               status_code=204,
               response_model=None)
async def delete_job(id: str):
    await service.delete_job(id)
