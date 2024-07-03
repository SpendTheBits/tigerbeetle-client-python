import ctypes
from ctypes import c_uint64, c_uint32, c_uint8, c_void_p, POINTER, Structure

# Load the shared library
lib = ctypes.CDLL('native/linux-x64/libtb_client.so')  # Adjust the path to your shared library

class TBAccount(Structure):
    _fields_ = [
        ('id', c_uint64),
        ('user_data_128', c_uint64 * 2),
        ('user_data_64', c_uint64),
        ('user_data_32', c_uint32),
        ('ledger', c_uint32),
        ('code', c_uint32),
        ('flags', c_uint32)
    ]

class TBTransfer(Structure):
    _fields_ = [
        ('id', c_uint64),
        ('debit_account_id', c_uint64),
        ('credit_account_id', c_uint64),
        ('amount', c_uint64),
        ('user_data_128', c_uint64 * 2),
        ('user_data_64', c_uint64),
        ('user_data_32', c_uint32),
        ('timeout', c_uint32),
        ('ledger', c_uint32),
        ('code', c_uint32),
        ('flags', c_uint32)
    ]

# Define function prototypes
lib.tb_client_create_accounts.argtypes = [c_void_p, POINTER(TBAccount), c_uint32]
lib.tb_client_create_accounts.restype = c_int

lib.tb_client_create_transfers.argtypes = [c_void_p, POINTER(TBTransfer), c_uint32]
lib.tb_client_create_transfers.restype = c_int

class Client:
    def __init__(self, addresses):
        self.addresses = addresses
        self.cluster_id = c_uint64(0)  # or appropriate initialization
        self.client = lib.tb_client_new(self.cluster_id, addresses)

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

# # Example usage
# if __name__ == "__main__":
#     addresses = ['127.0.0.1:3000']
#     client = Client(addresses)

#     accounts = [
#         TBAccount(id=137, user_data_128=(1, 0), user_data_64=1000, user_data_32=100, ledger=1, code=718, flags=0)
#     ]
#     client.create_accounts(accounts)

#     transfers = [
#         TBTransfer(id=1, debit_account_id=1, credit_account_id=2, amount=10, user_data_128=(2000, 0), user_data_64=200, user_data_32=2, timeout=0, ledger=1, code=1, flags=0)
   
