from fastapi import HTTPException

from app.opc_clients.clients import OpcClient, Snap7Client


def get_value_from_opc(opc_client: OpcClient, node_id: str):
    try:
        with opc_client as client:
            value = client.read_value(node_id=node_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return value


def get_value_from_plc(plc_client: Snap7Client, db_number: int, start: int, size: int):
    try:
        with plc_client as client:
            value = client.read_db(db_number=db_number, start=start, size=size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return value
