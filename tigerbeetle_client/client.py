# tigerbeetle_client/client.py

import requests
from typing import List

class UInt128:
    def __init__(self, high: int = 0, low: int = 0):
        self.high = high
        self.low = low

    def __repr__(self):
        return f"UInt128({self.high}, {self.low})"

    @staticmethod
    def zero() -> 'UInt128':
        return UInt128(0, 0)

class Account:
    def __init__(self, Id: UInt128, UserData128: UInt128, UserData64: int, UserData32: int, Ledger: int, Code: int, Flags: int):
        self.Id = Id
        self.UserData128 = UserData128
        self.UserData64 = UserData64
        self.UserData32 = UserData32
        self.Ledger = Ledger
        self.Code = Code
        self.Flags = Flags

    def to_dict(self):
        return {
            "Id": {"high": self.Id.high, "low": self.Id.low},
            "UserData128": {"high": self.UserData128.high, "low": self.UserData128.low},
            "UserData64": self.UserData64,
            "UserData32": self.UserData32,
            "Ledger": self.Ledger,
            "Code": self.Code,
            "Flags": self.Flags,
        }

class Transfer:
    def __init__(self, Id: UInt128, DebitAccountId: UInt128, CreditAccountId: UInt128, Amount: int, UserData128: UInt128, UserData64: int, UserData32: int, Timeout: int, Ledger: int, Code: int, Flags: int):
        self.Id = Id
        self.DebitAccountId = DebitAccountId
        self.CreditAccountId = CreditAccountId
        self.Amount = Amount
        self.UserData128 = UserData128
        self.UserData64 = UserData64
        self.UserData32 = UserData32
        self.Timeout = Timeout
        self.Ledger = Ledger
        self.Code = Code
        self.Flags = Flags

    def to_dict(self):
        return {
            "Id": {"high": self.Id.high, "low": self.Id.low},
            "DebitAccountId": {"high": self.DebitAccountId.high, "low": self.DebitAccountId.low},
            "CreditAccountId": {"high": self.CreditAccountId.high, "low": self.CreditAccountId.low},
            "Amount": self.Amount,
            "UserData128": {"high": self.UserData128.high, "low": self.UserData128.low},
            "UserData64": self.UserData64,
            "UserData32": self.UserData32,
            "Timeout": self.Timeout,
            "Ledger": self.Ledger,
            "Code": self.Code,
            "Flags": self.Flags,
        }

class Client:
    def __init__(self, cluster_id: UInt128, addresses: List[str]):
        self.cluster_id = cluster_id
        self.addresses = addresses

    def _request(self, endpoint: str, data: List[dict]):
        url = f"http://{self.addresses[0]}/{endpoint}"
        response = requests.post(url, json=data)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code}, {response.text}")
        return response.json()

    def create_accounts(self, accounts: List[Account]):
        data = [account.to_dict() for account in accounts]
        return self._request("create_accounts", data)

    def lookup_accounts(self, ids: List[UInt128]):
        data = [{"high": id.high, "low": id.low} for id in ids]
        return self._request("lookup_accounts", data)

    def create_transfers(self, transfers: List[Transfer]):
        data = [transfer.to_dict() for transfer in transfers]
        return self._request("create_transfers", data)

    def lookup_transfers(self, ids: List[UInt128]):
        data = [{"high": id.high, "low": id.low} for id in ids]
        return self._request("lookup_transfers", data)