import uuid
from sqlalchemy import String, UUID, Integer, Boolean, JSON
from sqlalchemy.orm import mapped_column, relationship

from app.database import Base


class OPCServer(Base):
    __tablename__ = "opc_servers"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = mapped_column(String(30), index=True)
    description = mapped_column(String(100))
    ip_address = mapped_column(String(30), index=True)
    port = mapped_column(Integer, index=True)
    node_id = mapped_column(JSON)
    enabled = mapped_column(Boolean, default=True, index=True)

    jobs = relationship("Job", back_populates="opc_servers")


class PLCServer(Base):
    __tablename__ = 'plc_servers'
    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = mapped_column(String(30), index=True)
    ip_address = mapped_column(String(30), index=True)
    port = mapped_column(Integer, index=True)
    db = mapped_column(Integer, index=True)
    rack = mapped_column(Integer, index=True)
    slot = mapped_column(Integer, index=True)
    offset = mapped_column(Integer, index=True)
    size = mapped_column(Integer, index=True)
    enabled = mapped_column(Boolean, default=True, index=True)

    jobs = relationship("Job", back_populates="plc_servers")
