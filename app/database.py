import re
from pymongo import MongoClient

from fastapi import HTTPException
from sqlalchemy import DateTime, func, Select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.sql.dml import Delete, ReturningInsert, ReturningUpdate

from app.config import settings


mongo_client = MongoClient(settings.mongodb_url)


class Base(DeclarativeBase):
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


async_engine = create_async_engine(
    url=settings.database_url,
    echo=True
)

session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def parse_error_message(error_message: str) -> str:
    still_referenced_pattern = re.compile(r"Key \((.*?)\)=\((.*?)\) is still referenced from table \"(.*?)\"\.")
    already_exists_pattern = re.compile(r"Key \((.*?)\)=\((.*?)\) already exists\.")
    invalid_fk_pattern = re.compile(r"Key \((.*?)\)=\((.*?)\) is not present in table \"(.*?)\"\.")

    still_referenced = still_referenced_pattern.search(error_message)
    unique_error = already_exists_pattern.search(error_message)
    invalid_fk = invalid_fk_pattern.search(error_message)

    if still_referenced:
        column = still_referenced.group(1)
        value = still_referenced.group(2)
        table = still_referenced.group(3)
        return f"Can't delete. Still referenced from table: {table}"

    elif unique_error:
        column = unique_error.group(1)
        value = unique_error.group(2)
        return f"Already exists: {column}"

    elif invalid_fk:
        column = invalid_fk.group(1)
        value = invalid_fk.group(2)
        table = invalid_fk.group(3)
        return f"Invalid foreign key: {column}"

    else:
        return error_message


async def get_all(statement: Select):
    async with session_factory() as session:
        result = await session.execute(statement)
        objs = result.scalars().all()
    return objs


async def get_one(statement: Select):
    async with session_factory() as session:
        result = await session.execute(statement)
        obj = result.scalar()
    return obj


async def execute_insert(statement: ReturningInsert):
    async with session_factory() as session:
        try:
            result = await session.execute(statement)
            obj = result.scalar_one()
        except IntegrityError as error:
            error_message = await parse_error_message(error.args[0])
            raise HTTPException(400, error_message)
        else:
            await session.commit()
    return obj


async def execute_update(statement: ReturningUpdate):
    async with session_factory() as session:
        try:
            result = await session.execute(statement)
            obj = result.scalar_one()
        except IntegrityError as error:
            error_message = await parse_error_message(error.args[0])
            raise HTTPException(400, error_message)
        except NoResultFound:
            raise HTTPException(404, "Not found")
        else:
            await session.commit()
    return obj


async def execute_delete(statement: Delete):
    async with session_factory() as session:
        try:
            await session.execute(statement)
        except IntegrityError as error:
            error_message = await parse_error_message(error.args[0])
            raise HTTPException(400, error_message)
        else:
            await session.commit()
