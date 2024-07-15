import ctypes
import platform

# Define the architecture and platform mapping
arch_map = {
    'x86_64': 'x86_64',
    'arm64': 'aarch64',
}

platform_map = {
    'linux': 'linux',
    'darwin': 'osx',
    'win32': 'win',
}
filename_map = {
    'linux': 'client.so',
    'darwin': 'libtb_client.dylib',
    'win32': 'client.dll',
}

# Get the current architecture and platform
arch = platform.machine()
os_platform = platform.system().lower()

# Construct the path to the shared library
binary_filename = f'./native/{platform_map[os_platform]}-{arch_map[arch]}/{filename_map[os_platform]}'

# Load the shared library
client_lib = ctypes.CDLL(binary_filename)

# Define the necessary structures
class tb_uint128_t(ctypes.Structure):
    _fields_ = [('high', ctypes.c_uint64), ('low', ctypes.c_uint64)]

class tb_account_t(ctypes.Structure):
    _fields_ = [
        ('id', tb_uint128_t),
        ('debits_pending', tb_uint128_t),
        ('debits_posted', tb_uint128_t),
        ('credits_pending', tb_uint128_t),
        ('credits_posted', tb_uint128_t),
        ('user_data_128', tb_uint128_t),
        ('user_data_64', ctypes.c_uint64),
        ('user_data_32', ctypes.c_uint32),
        ('reserved', ctypes.c_uint32),
        ('ledger', ctypes.c_uint32),
        ('code', ctypes.c_uint16),
        ('flags', ctypes.c_uint16),
        ('timestamp', ctypes.c_uint64),
    ]

class tb_create_accounts_result_t(ctypes.Structure):
    _fields_ = [
        ('index', ctypes.c_uint32),
        ('result', ctypes.c_uint32),
    ]

class tb_packet_t(ctypes.Structure):
    pass

tb_packet_t._fields_ = [
    ('next', ctypes.POINTER(tb_packet_t)),
    ('user_data', ctypes.c_void_p),
    ('operation', ctypes.c_uint8),
    ('status', ctypes.c_uint8),
    ('data_size', ctypes.c_uint32),
    ('data', ctypes.c_void_p),
    ('batch_next', ctypes.POINTER(tb_packet_t)),
    ('batch_tail', ctypes.POINTER(tb_packet_t)),
    ('batch_size', ctypes.c_uint32),
    ('reserved', ctypes.c_uint8 * 8),
]

# Define function prototypes
client_lib.tb_client_init.argtypes = [ctypes.POINTER(ctypes.c_void_p), tb_uint128_t, ctypes.c_char_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p, ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(tb_packet_t), ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32)]
client_lib.tb_client_init.restype = ctypes.c_int

client_lib.tb_client_acquire_packet.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.POINTER(tb_packet_t))]
client_lib.tb_client_acquire_packet.restype = ctypes.c_int

client_lib.tb_client_release_packet.argtypes = [ctypes.c_void_p, ctypes.POINTER(tb_packet_t)]
client_lib.tb_client_release_packet.restype = None

client_lib.tb_client_submit.argtypes = [ctypes.c_void_p, ctypes.POINTER(tb_packet_t)]
client_lib.tb_client_submit.restype = None

client_lib.tb_client_deinit.argtypes = [ctypes.c_void_p]
client_lib.tb_client_deinit.restype = None

# Example: Class to wrap around the client library
class TigerBeetleClient:
    def __init__(self, lib):
        self.lib = lib
        self.context = ctypes.c_void_p()
        self.init_client()

    def init_client(self):
        cluster_id = tb_uint128_t(0, 1)  # Example cluster ID
        address = b'127.0.0.1:3000'  # Example address
        packets_count = 1024
        on_completion_ctx = ctypes.c_void_p()
        on_completion_fn = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(tb_packet_t), ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32)(self.on_completion)
        result = self.lib.tb_client_init(ctypes.byref(self.context), cluster_id, address, len(address), packets_count, on_completion_ctx, on_completion_fn)
        if result != 0:
            raise RuntimeError("Failed to initialize client")

    def on_completion(self, context, client, packet, data, size):
        # Handle completion (dummy implementation)
        pass

    def create_accounts(self, accounts):
        # Acquire a packet
        packet = ctypes.POINTER(tb_packet_t)()
        acquire_status = self.lib.tb_client_acquire_packet(self.context, ctypes.byref(packet))
        if acquire_status != 0:
            raise RuntimeError("Failed to acquire packet")

        # Fill packet with account data
        packet.contents.operation = 129  # TB_OPERATION_CREATE_ACCOUNTS
        packet.contents.data_size = ctypes.sizeof(tb_account_t) * len(accounts)
        packet.contents.data = ctypes.cast((tb_account_t * len(accounts))(*accounts), ctypes.c_void_p)

        # Submit the packet
        self.lib.tb_client_submit(self.context, packet)

        # Release the packet
        self.lib.tb_client_release_packet(self.context, packet)

    def deinit(self):
        self.lib.tb_client_deinit(self.context)

# Example usage
if __name__ == "__main__":
    client = TigerBeetleClient(client_lib)

    # Create example accounts
    accounts = [
        tb_account_t(id=tb_uint128_t(0, 1), debits_pending=tb_uint128_t(0, 0), debits_posted=tb_uint128_t(0, 0), credits_pending=tb_uint128_t(0, 0), credits_posted=tb_uint128_t(0, 0), user_data_128=tb_uint128_t(0, 0), user_data_64=0, user_data_32=0, reserved=0, ledger=1, code=1, flags=0, timestamp=0),
        tb_account_t(id=tb_uint128_t(0, 2), debits_pending=tb_uint128_t(0, 0), debits_posted=tb_uint128_t(0, 0), credits_pending=tb_uint128_t(0, 0), credits_posted=tb_uint128_t(0, 0), user_data_128=tb_uint128_t(0, 0), user_data_64=0, user_data_32=0, reserved=0, ledger=1, code=1, flags=0, timestamp=0),
    ]

    client.create_accounts(accounts)
    print("Accounts created successfully")
    client.deinit()
