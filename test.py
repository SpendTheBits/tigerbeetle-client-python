from tigerbeetle_client.client1 import Client,TBAccount


tb_client = Client( ["127.0.0.1:3000"])
# tb_client.lookup_accounts([UInt128(0, 137)])
tb_account  =     TBAccount(id=137, user_data_128=(1, 0), user_data_64=1000, user_data_32=100, ledger=1, code=718, flags=0)
tb_client.create_accounts([tb_account])

# new_acc =Account(Id=UInt128(0, 137), UserData128=UInt128(0, 1), UserData64=1000, UserData32=100, Ledger=1, Code=718, Flags=0)
# tb_client.create_accounts([new_acc])

