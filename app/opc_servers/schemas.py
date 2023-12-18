from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, constr, model_validator
from uuid import UUID


class OpcNodeID(BaseModel):
    namespace: int
    server: str
    variable: str = None

    def to_string(self):
        variable_part = f'."{self.variable}"' if self.variable is not None else ''
        return f'ns={self.namespace};s="{self.server}"{variable_part}'

    def to_dict(self):
        return {
            'ns': self.namespace,
            's': self.server,
            'variable': self.variable
        }


class OpcServerCreate(BaseModel):
    name: constr(min_length=3, max_length=30)
    description: constr(min_length=3, max_length=100)
    ip_address: constr(min_length=7, max_length=30)
    port: int
    node_id: OpcNodeID
    enabled: bool = True


class OpcServerUpdate(BaseModel):
    name: constr(min_length=3, max_length=30) = None
    description: constr(min_length=3, max_length=100) = None
    ip_address: constr(min_length=7, max_length=30) = None
    port: int = None
    node_id: OpcNodeID = None
    enabled: bool = None

    @model_validator(mode="after")
    def check_fields(self):
        update_data = self.model_dump(exclude_none=True)
        if not update_data:
            raise HTTPException(400, "No data to update")
        return self


class OpcServerSchema(BaseModel):
    id: UUID
    name: constr(min_length=3, max_length=30)
    description: constr(min_length=3, max_length=100)
    ip_address: constr(min_length=7, max_length=30)
    port: int
    node_id: OpcNodeID
    enabled: bool = True

    model_config = ConfigDict(from_attributes=True)


class PlcServerCreate(BaseModel):
    name: constr(min_length=3, max_length=30)
    ip_address: constr(min_length=7, max_length=30)
    port: int
    db: int
    rack: int
    slot: int
    offset: int
    size: int
    enabled: bool = True


class PlcServerUpdate(BaseModel):
    name: constr(min_length=3, max_length=30) = None
    ip_address: constr(min_length=7, max_length=30) = None
    port: int = None
    db: int = None
    rack: int = None
    slot: int = None
    offset: int = None
    size: int = None
    enabled: bool = None

    @model_validator(mode="after")
    def check_fields(self):
        update_data = self.model_dump(exclude_none=True)
        if not update_data:
            raise HTTPException(400, "No data to update")
        return self


class PlcServerSchema(PlcServerCreate):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
