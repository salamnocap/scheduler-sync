from opcua import Client
import snap7
import snap7.util as util


class OpcClient:
    def __init__(self, ip_address: str, port: int):
        self.opc_url = f"opc.tcp://{ip_address}:{port}"
        self.client = None

    def connect(self):
        if self.client is None:
            self.client = Client(self.opc_url)
        self.client.connect()

    def disconnect(self):
        if self.client is not None:
            self.client.disconnect()
            self.client = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def read_value(self, node_id: str):
        if self.client is None:
            raise Exception("Not connected to OPC server.")
        node = self.client.get_node(node_id)
        value = node.get_value()
        if value is None:
            raise Exception("No data available for the specified Node ID.")
        return value


class Snap7Client:
    def __init__(self, ip: str, rack: int, slot: int):
        self.ip = ip
        self.rack = rack
        self.slot = slot
        self.client = snap7.client.Client()

    def connect(self):
        self.client.connect(self.ip, self.rack, self.slot)

    def disconnect(self):
        self.client.disconnect()
        self.client.destroy()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def read_db(self, db_number: int, start: int, size: int):
        if not self.client.get_connected():
            raise Exception("Not connected to PLC.")
        byte_array = self.client.db_read(db_number, start, size)
        return util.get_real(byte_array, 0)
