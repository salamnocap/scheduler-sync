from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, constr, model_validator
from pydantic import BaseModel, validator


class PeriodicTask(BaseModel):
    interval: int = None
    interval_unit: str = None


class CronTask(BaseModel):
    day_of_week: int = None
    hour: int = None
    minute: int = None
    second: int = None


class JobDetails(BaseModel):
    job_type: str
    periodic_task: PeriodicTask = None
    cron_task: CronTask = None

    class Config:
        allow_values = {"cron", "periodic"}

        @classmethod
        def validate(cls, job_type):
            if job_type not in cls.allow_values:
                raise ValueError(f"Invalid job_type. Allowed values are: {', '.join(cls.allow_values)}")
            return job_type

    @validator("cron_task", pre=True, always=True)
    def check_cron_task(cls, cron_task, values):
        job_type = values.get("job_type")
        if job_type == "cron" and not any(cron_task.values()):
            raise ValueError("At least one field must be filled for cron_task when job_type is 'cron'")
        return cron_task

    @validator("periodic_task", pre=True, always=True)
    def check_periodic_task(cls, periodic_task, values):
        job_type = values.get("job_type")
        if job_type == "periodic" and not all(periodic_task.values()):
            raise ValueError("All fields must be filled for periodic_task when job_type is 'periodic'")
        return periodic_task


class JobCreate(BaseModel):
    name: constr(min_length=3, max_length=30)
    description: constr(min_length=3, max_length=100)
    job_type: constr(min_length=3, max_length=10)
    details: JobDetails
    opc_id: str = None
    plc_id: str = None

    @model_validator(mode="after")
    def check_fields(self):
        if not self.opc_id and not self.plc_id:
            raise HTTPException(400, "opc_id or plc_id must be not null")
        return self


class JobSchema(JobCreate):
    id: str
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ConfigDict: lambda v: dict(v),
        }
