import ctypes
from ctypes import c_uint64, c_uint32, c_void_p, POINTER, Structure, byref, c_char_p

# Define structures based on tb_client.h
class UInt128(Structure):
    _fields_ = [("high", c_uint64), ("low", c_uint64)]

class TBAccount(Structure):
    _fields_ = [
        ("id", UInt128),
        ("user_data_128", UInt128),
        ("user_data_64", c_uint64),
        ("user_data_32", c_uint32),
        ("ledger", c_uint32),
        ("code", c_uint32),
        ("flags", c_uint32),
    ]

class TBTransfer(Structure):
    _fields_ = [
        ("id", UInt128),
        ("debit_account_id", UInt128),
        ("credit_account_id", UInt128),
        ("amount", c_uint64),
        ("user_data_128", UInt128),
        ("user_data_64", c_uint64),
        ("user_data_32", c_uint32),
        ("timeout", c_uint32),
        ("ledger", c_uint32),
        ("code", c_uint32),
        ("flags", c_uint32),
    ]

# Load the shared library
lib = ctypes.CDLL('native/linux-x64/libtb_client.so')  # Adjust the path to your shared library

# Define function prototypes
lib.tb_client_create_accounts.argtypes = [c_void_p, POINTER(TBAccount), c_uint32]
lib.tb_client_create_accounts.restype = c_int

lib.tb_client_create_transfers.argtypes = [c_void_p, POINTER(TBTransfer), c_uint32]
lib.tb_client_create_transfers.restype = c_int

lib.tb_client_new.argtypes = [UInt128, POINTER(c_char_p), c_uint32]
lib.tb_client_new.restype = c_void_p

lib.tb_client_free.argtypes = [c_void_p]
lib.tb_client_free.restype = None

class Client:
    def __init__(self, cluster_id: UInt128, addresses: list):
        address_array = (c_char_p * len(addresses))(*[addr.encode('utf-8') for addr in addresses])
        self.client = lib.tb_client_new(cluster_id, address_array, len(addresses))

    def __del__(self):
        lib.tb_client_free(self.client)

    def create_accounts(self, accounts):
        account_array = (TBAccount * len(accounts))(*accounts)
        result = lib.tb_client_create_accounts(self.client, account_array, len(accounts))
        if result != 0:
            raise Exception(f"Error creating accounts: {result}")

    def create_transfers(self, transfers):
        transfer_array = (TBTransfer * len(transfers))(*transfers)
        result = lib.tb_client_create_transfers(self.client, transfer_array, len(transfers))
        if result != 0:
            raise Exception(f"Error creating transfers: {result}")

# Example usage
# if __name__ == "__main__":
#     cluster_id = UInt128(0, 0)
#     addresses = ['127.0.0.1:3000']
    
#     client = Client(cluster_id, addresses)
    
#     accounts = [
#         TBAccount(id=UInt128(0, 137), user_data_128=UInt128(0, 1), user_data_64=1000, user_data_32=100, ledger=1, code=718, flags=0)
#     ]
#     client.create_accounts(accounts)

#     transfers = [
#         TBTransfer(id=UInt128(0, 1), debit_account_id=UInt128(0, 1), credit_account_id=UInt128(0, 2), amount=10, user_data_128=UInt128(0, 2000), user_data_64=200, user_data_32=2, timeout=0, ledger=1, code=1, flags=0)
#     ]
#     client.create_transfers(transfers)
