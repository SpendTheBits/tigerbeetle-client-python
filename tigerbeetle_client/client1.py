import ctypes
from ctypes import c_uint64, c_uint32, c_void_p, POINTER, Structure, byref, c_char_p, c_uint8, c_uint16, c_int

# Define structures based on tb_client.h
class UInt128(ctypes.Structure):
    _fields_ = [("high", c_uint64), ("low", c_uint64)]

class TBAccount(ctypes.Structure):
    _fields_ = [
        ("id", UInt128),
        ("debits_pending", UInt128),
        ("debits_posted", UInt128),
        ("credits_pending", UInt128),
        ("credits_posted", UInt128),
        ("user_data_128", UInt128),
        ("user_data_64", c_uint64),
        ("user_data_32", c_uint32),
        ("reserved", c_uint32),
        ("ledger", c_uint32),
        ("code", c_uint16),
        ("flags", c_uint16),
        ("timestamp", c_uint64)
    ]

class TBTransfer(ctypes.Structure):
    _fields_ = [
        ("id", UInt128),
        ("debit_account_id", UInt128),
        ("credit_account_id", UInt128),
        ("amount", UInt128),
        ("pending_id", UInt128),
        ("user_data_128", UInt128),
        ("user_data_64", c_uint64),
        ("user_data_32", c_uint32),
        ("timeout", c_uint32),
        ("ledger", c_uint32),
        ("code", c_uint16),
        ("flags", c_uint16),
        ("timestamp", c_uint64)
    ]

class TBPacket(ctypes.Structure):
    pass

TBPacket._fields_ = [
    ("next", POINTER(TBPacket)),
    ("user_data", c_void_p),
    ("operation", c_uint8),
    ("status", c_uint8),
    ("data_size", c_uint32),
    ("data", c_void_p),
    ("batch_next", POINTER(TBPacket)),
    ("batch_tail", POINTER(TBPacket)),
    ("batch_size", c_uint32),
    ("reserved", c_uint8 * 8)
]

# Load the shared library
lib = ctypes.CDLL('native/linux-x64/libtb_client.so')  # Adjust the path to your shared library

# Define function prototypes based on tb_client.h
lib.tb_client_init.argtypes = [POINTER(c_void_p), UInt128, c_char_p, c_uint32, c_uint32, c_void_p, c_void_p]
lib.tb_client_init.restype = c_int

lib.tb_client_acquire_packet.argtypes = [c_void_p, POINTER(POINTER(TBPacket))]
lib.tb_client_acquire_packet.restype = c_int

lib.tb_client_submit.argtypes = [c_void_p, POINTER(TBPacket)]
lib.tb_client_submit.restype = None

lib.tb_client_deinit.argtypes = [c_void_p]
lib.tb_client_deinit.restype = None

class Client:
    def __init__(self, cluster_id: UInt128, addresses: list):
        self.client = c_void_p()
        address_str = addresses[0].encode('utf-8')
        result = lib.tb_client_init(byref(self.client), cluster_id, address_str, len(address_str), 1, None, None)
        if result != 0:
            raise Exception(f"Error initializing client: {result}")

    def __del__(self):
        if self.client:
            lib.tb_client_deinit(self.client)

    def create_accounts(self, accounts):
        for account in accounts:
            packet = POINTER(TBPacket)()
            result = lib.tb_client_acquire_packet(self.client, byref(packet))
            if result != 0:
                raise Exception(f"Error acquiring packet: {result}")

            packet.contents.operation = 129  # TB_OPERATION_CREATE_ACCOUNTS
            packet.contents.data_size = ctypes.sizeof(TBAccount)
            packet.contents.data = ctypes.cast(ctypes.pointer(account), c_void_p)

            lib.tb_client_submit(self.client, packet)

    def create_transfers(self, transfers):
        for transfer in transfers:
            packet = POINTER(TBPacket)()
            result = lib.tb_client_acquire_packet(self.client, byref(packet))
            if result != 0:
                raise Exception(f"Error acquiring packet: {result}")

            packet.contents.operation = 130  # TB_OPERATION_CREATE_TRANSFERS
            packet.contents.data_size = ctypes.sizeof(TBTransfer)
            packet.contents.data = ctypes.cast(ctypes.pointer(transfer), c_void_p)

            lib.tb_client_submit(self.client, packet)

# # Example usage
# if __name__ == "__main__":
#     cluster_id = UInt128(0, 0)
#     addresses = ['127.0.0.1:3000']
    
#     client = Client(cluster_id, addresses)
    
#     accounts = [
#         TBAccount(
#             id=UInt128(0, 137),
#             debits_pending=UInt128(0, 0),
#             debits_posted=UInt128(0, 0),
#             credits_pending=UInt128(0, 0),
#             credits_posted=UInt128(0, 0),
#             user_data_128=UInt128(0, 1),
#             user_data_64=1000,
#             user_data_32=100,
#             reserved=0,
#             ledger=1,
#             code=718,
#             flags=0,
#             timestamp=0
#         )
#     ]
#     client.create_accounts(accounts)

#     transfers = [
#         TBTransfer(
#             id=UInt128(0, 1),
#             debit_account_id=UInt128(0, 1),
#             credit_account_id=UInt128(0, 2),
#             amount=UInt128(0, 10),
#             pending_id=UInt128(0, 0),
#             user_data_128=UInt128(0, 2000),
#             user_data_64=200,
#             user_data_32=2,
#             timeout=0,
#             ledger=1,
#             code=1,
#             flags=0,
#             timestamp=0
#         )
#     ]
#     client.create_transfers(transfers)
