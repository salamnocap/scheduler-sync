import datetime

from fastapi import HTTPException
from pydantic import ConfigDict, constr, model_validator, BaseModel, conint
from typing import Literal
from uuid import UUID
from datetime import datetime


class PeriodicTask(BaseModel):
    interval: int

    @model_validator(mode='after')
    def validate_fields(self):
        interval = self.interval

        if not (0 < interval < 60):
            raise ValueError("Interval must be greater than 0 and less than 60 minutes")

        return self


class CronTask(BaseModel):
    day_of_week: conint(ge=0, lt=7) | None = "*"
    hour: conint(ge=0, lt=24) | None = "*"
    minute: conint(ge=0, lt=60) | None = "*"

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
            "datetime": self.datetime.now(),
            "value": self.value,
            "difference": self.difference
        }
