import ctypes
from ctypes import c_uint64, c_uint32, c_uint16, c_void_p, POINTER, Structure, byref, c_char_p, c_uint8, c_int
import struct

# Define UInt128 structure
class UInt128(ctypes.Structure):
    _fields_ = [("high", c_uint64), ("low", c_uint64)]
    _pack_ = 1  # Ensure correct alignment

# Define the TBAccount structure based on the C header definition
class TBAccount(ctypes.Structure):
    _fields_ = [
        ("id", UInt128),
        ("debits_pending", UInt128),
        ("debits_posted", UInt128),
        ("credits_pending", UInt128),
        ("credits_posted", UInt128),
        ("user_data", UInt128),
        ("reserved", c_uint32 * 4),  # 4*32=128
        ("ledger", c_uint32),
        ("code", c_uint16),
        ("flags", c_uint16),
        ("timestamp", c_uint64),
    ]
    _pack_ = 1  # Ensure correct alignment

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
TBPacket._pack_ = 1  # Ensure correct alignment

from libtb import LIBTB_CLIENT_PATH
# Load the shared library
lib = ctypes.CDLL(LIBTB_CLIENT_PATH)

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
        print(f"Client initialized with cluster_id={cluster_id} and addresses={addresses}")

    def __del__(self):
        if self.client:
            lib.tb_client_deinit(self.client)
            print("Client deinitialized")

    def create_accounts(self, accounts):
        for account in accounts:
            packet = POINTER(TBPacket)()
            result = lib.tb_client_acquire_packet(self.client, byref(packet))
            if result != 0:
                raise Exception(f"Error acquiring packet: {result}")
            print(f"Packet acquired: {packet}")

            packet.contents.operation = 129  # TB_OPERATION_CREATE_ACCOUNTS
            packet.contents.data_size = ctypes.sizeof(TBAccount)
            
            # Handle endianness
            packed_data = self.pack_account(account)
            packet.contents.data = ctypes.cast(ctypes.create_string_buffer(packed_data), c_void_p)
            print(f"Packet prepared with operation={packet.contents.operation} and data_size={packet.contents.data_size}")

            # Print debug information
            print(f"Submitting account: {account}")
            print(f"Account size: {ctypes.sizeof(TBAccount)}")
            print(f"Packet operation: {packet.contents.operation}")
            print(f"Packet data size: {packet.contents.data_size}")
            print(f"Packet data: {bytes(ctypes.string_at(packet.contents.data, packet.contents.data_size))}")

            # Print individual field values for debugging
            print(f"id_high: {account.id.high}, id_low: {account.id.low}")
            print(f"debits_pending_high: {account.debits_pending.high}, debits_pending_low: {account.debits_pending.low}")
            print(f"debits_posted_high: {account.debits_posted.high}, debits_posted_low: {account.debits_posted.low}")
            print(f"credits_pending_high: {account.credits_pending.high}, credits_pending_low: {account.credits_pending.low}")
            print(f"credits_posted_high: {account.credits_posted.high}, credits_posted_low: {account.credits_posted.low}")
            print(f"user_data_high: {account.user_data.high}, user_data_low: {account.user_data.low}")
            print(f"reserved: {account.reserved[:]}")
            print(f"ledger: {account.ledger}")
            print(f"code: {account.code}")
            print(f"flags: {account.flags}")
            print(f"timestamp: {account.timestamp}")

            lib.tb_client_submit(self.client, packet)
            print("Packet submitted")

    def pack_account(self, account):
        # Packing the account with little-endian format
        packed_data = struct.pack(
            '<QQQQQQQQIIIIHHQ',  # Little-endian format for all fields
            account.id.high, account.id.low,
            account.debits_pending.high, account.debits_pending.low,
            account.debits_posted.high, account.debits_posted.low,
            account.credits_pending.high, account.credits_pending.low,
            account.credits_posted.high, account.credits_posted.low,
            account.user_data.high, account.user_data.low,
            *account.reserved,
            account.ledger, account.code, account.flags, account.timestamp
        )
        return packed_data

# Verify sizes
print(f"Size of TBAccount: {ctypes.sizeof(TBAccount)}")  # Should be 128

# Example usage
if __name__ == "__main__":
    cluster_id = UInt128(0, 0)
    addresses = ['127.0.0.1:3000']
    
    client = Client(cluster_id, addresses)
    
    accounts = [
        TBAccount(
            id=UInt128(0, 137),
            debits_pending=UInt128(0, 0),
            debits_posted=UInt128(0, 0),
            credits_pending=UInt128(0, 0),
            credits_posted=UInt128(0, 0),
            user_data=UInt128(0, 1),
            reserved=(c_uint32 * 4)(),  # Initialize reserved with correct size
            ledger=1,
            code=718,
            flags=0,
            timestamp=0
        )
    ]
    client.create_accounts(accounts)
