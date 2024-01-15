from pymongo import DESCENDING

from app.database import mongo_client


def create_collection(db_name: str, collection_name: str) -> None:
    mongo_client[db_name].create_collection(collection_name)


def delete_collection(db_name: str, collection_name: str) -> None:
    mongo_client[db_name].drop_collection(collection_name)


def get_last_document(db_name: str, collection_name: str) -> dict or None:
    return mongo_client[db_name][collection_name].find_one(sort=[('_id', DESCENDING)])


def get_collection(db_name: str,
                   collection_name: str,
                   sort_by: str = None,
                   sort_order: int = DESCENDING,
                   limit: int = 100,
                   skip: int = 0):
    collection = mongo_client[db_name][collection_name]

    if sort_by:
        cursor = collection.find().sort(sort_by, sort_order).skip(skip).limit(limit)
    else:
        cursor = collection.find().skip(skip).limit(limit)

    result = []
    for document in cursor:
        document['_id'] = str(document['_id'])
        result.append(document)

    return result


def get_db_collections(db_name: str) -> list[str]:
    return mongo_client[db_name].list_collection_names()


def create_document(db_name: str, collection_name: str, document: dict) -> None:
    collection = mongo_client[db_name][collection_name]
    collection.insert_one(document)


def delete_document(db_name: str, collection_name: str, document_id: str) -> None:
    collection = mongo_client[db_name][collection_name]
    collection.delete_one({"_id": document_id})
