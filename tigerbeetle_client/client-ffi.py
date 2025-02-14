import cffi

ffi = cffi.FFI()

# Define the C header
ffi.cdef("""
typedef struct {
    uint64_t field1;
    uint32_t field2;
    uint16_t field3;
    // Other fields...
} context_t;

typedef struct {
    context_t context;
    uint64_t some_other_field;
    uint32_t another_field;
    // Other fields...
} tb_client_t;

typedef struct {
    uint64_t id;
    uint64_t user_data;
    uint64_t reserved;
    uint64_t credits_posted;
    uint64_t credits_pending;
    uint64_t debits_posted;
    uint64_t debits_pending;
    uint64_t timestamp;
    uint32_t ledger;
    uint32_t code;
} tb_account_t;

typedef struct {
    uint32_t size;
    uint32_t version;
    uint32_t max_credits;
    uint32_t max_debits;
    uint64_t max_balance;
} tb_client_config_t;

void* tb_client_init(const char* server_ip, uint16_t server_port, uint16_t cluster_id, tb_client_config_t* config);
void tb_client_deinit(void* client_handle);
int tb_client_submit(void* client_handle, tb_account_t* account, size_t account_count);
int tb_client_acquire_packet(void* client_handle, tb_account_t* account, size_t account_count);
void* tb_client_completion_context(void* client_handle);
void tb_client_release_packet(void* client_handle);
int tb_client_init_echo(void* client_handle, const char* message);
""")

# Load the shared library
C = ffi.dlopen("native/osx-aarch64/libtb_client.dylib")

# Example usage
def main():
    server_ip = "127.0.0.1"
    server_port = 3000
    cluster_id = 1

    config = ffi.new("tb_client_config_t *", {
        'size': ffi.sizeof("tb_client_config_t"),
        'version': 1,
        'max_credits': 1000000,
        'max_debits': 1000000,
        'max_balance': 1000000000000000
    })

    client_handle = C.tb_client_init(server_ip.encode('utf-8'), server_port, cluster_id, config)
    if client_handle == ffi.NULL:
        raise Exception("Failed to initialize the TigerBeetle client.")

    account = ffi.new("tb_account_t *", {
        'id': 1234,
        'user_data': 5678,
        'reserved': 0,
        'credits_posted': 0,
        'credits_pending': 0,
        'debits_posted': 0,
        'debits_pending': 0,
        'timestamp': 0,
        'ledger': 1,
        'code': 1001
    })

    result = C.tb_client_submit(client_handle, account, 1)
    if result != 0:
        raise Exception(f"Failed to submit account: {result}")

    C.tb_client_deinit(client_handle)

if __name__ == "__main__":
    main()
