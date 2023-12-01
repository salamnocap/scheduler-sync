from sqlalchemy import select, insert, delete

from app.database import get_all, get_one, execute_insert, execute_delete
from app.jobs.models import Job
from app.jobs.schemas import JobCreate, JobSchema


async def get_jobs() -> list[JobSchema]:
    statement = select(Job)
    jobs = await get_all(statement)
    return jobs


async def get_job(id: str) -> JobSchema | None:
    statement = select(Job).where(Job.id == id)
    job = await get_one(statement)
    return job


async def create_job(data: JobCreate) -> JobSchema:
    statement = insert(Job).values(data.model_dump()).returning(Job)
    job_id = await execute_insert(statement)
    return await get_job(job_id)


async def delete_job(id: str) -> None:
    statement = delete(Job).where(Job.id == id)
    await execute_delete(statement)
