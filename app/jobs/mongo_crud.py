from pymongo import DESCENDING
from pymongo.cursor import Cursor

from app.database import mongo_client
from app.config import settings


def create_collection(collection_name: str) -> None:
    mongo_client[settings.mongodb_db].create_collection(collection_name)


def delete_collection(collection_name: str) -> None:
    mongo_client[settings.mongodb_db].drop_collection(collection_name)


def get_last_document(collection_name: str) -> dict:
    collection = mongo_client[settings.mongodb_db][collection_name]
    return collection.find().sort("_id", DESCENDING).limit(1)[0]


def get_collection(collection_name: str,
                   sort_by: str = None,
                   sort_order: int = DESCENDING,
                   limit: int = 100,
                   skip: int = 0) -> Cursor:
    collection = mongo_client[settings.mongodb_db][collection_name]
    if sort_by:
        return collection.find().sort(sort_by, sort_order).skip(skip).limit(limit)
    else:
        return collection.find().skip(skip).limit(limit)


def create_document(collection_name: str, document: dict):
    collection = mongo_client[settings.mongodb_db][collection_name]
    collection.insert_one(document)


def delete_document(collection_name: str, document_id: str):
    collection = mongo_client[settings.mongodb_db][collection_name]
    collection.delete_one({"_id": document_id})

