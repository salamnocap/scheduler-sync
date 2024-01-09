import pytz
from fastapi import HTTPException
from pydantic import ConfigDict, constr, model_validator, BaseModel, conint
from typing import Literal
from uuid import UUID
from datetime import datetime

from app.config import settings


class PeriodicTask(BaseModel):
    metric: Literal["seconds", "minutes", "hours", "days", "weeks"]
    interval: int


class CronTask(BaseModel):
    day: conint(ge=1, le=31) | str | None = "*"
    week: conint(ge=1, le=53) | str | None = "*"
    day_of_week: conint(ge=0, le=6) | str | None = "*"
    hour: conint(ge=0, le=23) | str | None = "*"
    minute: conint(ge=0, le=59) | str | None = "*"
    second: conint(ge=0, le=59) | str | None = "*"

    @classmethod
    def validate(cls, **kwargs):
        if not kwargs:
            raise ValueError("At least one of the following parameters must be not null: "
                             "day_of_week, hour, minute, second")
        return kwargs


class JobDetails(BaseModel):
    job_type: Literal["periodic", "cron"]
    periodic_task: PeriodicTask | None = None
    cron_task: CronTask | None = None

    @model_validator(mode='after')
    def validate_fields(self):
        if self.job_type == "periodic" and self.periodic_task is None:
            raise ValueError("periodic_task must be not null")
        elif self.job_type == "cron" and self.cron_task is None:
            raise ValueError("cron_task must be not null")

        if self.periodic_task is None and self.cron_task is None:
            raise ValueError("At least one of the following parameters must be not null: "
                             "periodic_task, cron_task")
        elif self.periodic_task is not None and self.cron_task is not None:
            raise ValueError("Only one of the following parameters must be not null: "
                             "periodic_task, cron_task")

        return self


class JobCreate(BaseModel):
    name: constr(min_length=3, max_length=30, pattern=r'^[a-zA-Z0-9]*$')
    description: constr(min_length=3, max_length=100)
    details: JobDetails
    opc_id: UUID | None = None
    plc_id: UUID | None = None

    @model_validator(mode="after")
    def check_fields(self):
        if not self.opc_id and not self.plc_id:
            raise HTTPException(400, "At least one of the following parameters must "
                                     "be not null: opc_id, plc_id")
        return self


class JobSchemaConfig:
    model_config = ConfigDict(from_attributes=True)


class JobSchema(JobCreate, JobSchemaConfig):
    id: int
    created_at: datetime
    updated_at: datetime


class DataSchema(BaseModel):
    datetime: datetime
    value: float

    def to_dict(self):
        return {
            "datetime": self.datetime.now(),
            "value": self.value
        }


class DataSchemaWDiff(BaseModel):
    datetime: datetime
    value: float
    difference: float

    def to_dict(self):
        return {
            "datetime": self.datetime.replace(tzinfo=pytz.timezone(settings.timezone)),
            "value": self.value,
            "difference": self.difference
        }
