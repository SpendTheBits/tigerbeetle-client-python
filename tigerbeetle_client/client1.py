import ctypes
from ctypes import c_uint64, c_uint32, c_uint16, c_void_p, POINTER, Structure, byref, c_char_p, c_uint8, c_int
import platform
import os

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
        ("user_data_128", UInt128),
        ("user_data_64", c_uint64),
        ("user_data_32", c_uint32),
        ("reserved", c_uint32),
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

# Define the library path dynamically based on platform and architecture
def get_library_path():
    arch_map = {
        "arm64": "aarch64",
        "x86_64": "x86_64"
    }

    platform_map = {
        "Linux": "linux",
        "Darwin": "macos",
        "Windows": "windows",
    }

    arch = platform.machine()
    plat = platform.system()

    if arch not in arch_map:
        raise Exception(f"Unsupported arch: {arch}")

    if plat not in platform_map:
        raise Exception(f"Unsupported platform: {plat}")

    extra = ''
    if plat == "Linux":
        extra = '-gnu'
        if os.path.exists("/proc/self/map_files/"):
            for file in os.listdir("/proc/self/map_files/"):
                real_path = os.readlink(os.path.join("/proc/self/map_files/", file))
                if 'musl' in real_path:
                    extra = '-musl'
                    break

    filename = f"./bin/{arch_map[arch]}-{platform_map[plat]}{extra}/client.node"
    return filename

# Load the shared library
LIBTB_CLIENT_PATH = get_library_path()
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
        address_str = ",".join(addresses).encode('utf-8')
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
            
            packed_data = self.pack_account(account)
            packet.contents.data = ctypes.cast(ctypes.create_string_buffer(packed_data), c_void_p)
            print(f"Packet prepared with operation={packet.contents.operation} and data_size={packet.contents.data_size}")

            try:
                lib.tb_client_submit(self.client, packet)
                print("Packet submitted successfully")
            except Exception as e:
                print(f"Error submitting packet: {e}")

    def pack_account(self, account):
        # Packing the account with little-endian format
        packed_data = struct.pack(
            '<QQQQQQQQQQQQIIIIHHQ',  # Little-endian format for all fields
            account.id.high, account.id.low,
            account.debits_pending.high, account.debits_pending.low,
            account.debits_posted.high, account.debits_posted.low,
            account.credits_pending.high, account.credits_pending.low,
            account.credits_posted.high, account.credits_posted.low,
            account.user_data_128.high, account.user_data_128.low,
            account.user_data_64, account.user_data_32,
            account.reserved, account.ledger, account.code, account.flags, account.timestamp
        )
        return packed_data

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
            user_data_128=UInt128(0, 1),
            user_data_64=0,
            user_data_32=0,
            reserved=0,  # Initialize reserved with correct size
            ledger=1,
            code=718,
            flags=0,
            timestamp=0
        )
    ]
    client.create_accounts(accounts)
