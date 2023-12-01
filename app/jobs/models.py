from sqlalchemy import String, Integer, ForeignKey, JSON, UUID
from sqlalchemy.orm import mapped_column, relationship

from app.database import Base


class Job(Base):
    __tablename__ = 'jobs'
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(30))
    description = mapped_column(String(100))
    job_type = mapped_column(String(10))
    details = mapped_column(JSON)
    opc_id = mapped_column(UUID(as_uuid=True),
                           ForeignKey("opc_servers.id", ondelete="CASCADE"),
                           index=True,
                           nullable=True)
    plc_id = mapped_column(UUID(as_uuid=True),
                           ForeignKey("plc_servers.id", ondelete="CASCADE"),
                           index=True,
                           nullable=True)

    opc_servers = relationship("OPCServer", back_populates="jobs")
    plc_servers = relationship("PLCServer", back_populates="jobs")
