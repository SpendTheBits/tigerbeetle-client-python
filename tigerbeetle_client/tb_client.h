// tb_client.h
#ifndef TB_CLIENT_H
#define TB_CLIENT_H

#include <stdint.h>

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

#endif // TB_CLIENT_H
