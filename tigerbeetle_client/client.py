import socket
import struct
from dataclasses import dataclass, asdict

# Define the operation codes based on the protocol
OP_CREATE_ACCOUNTS = 1
OP_CREATE_TRANSFERS = 2

# Define the header format constants
HEADER_FORMAT = '>IHHI'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

# Define the account and transfer structures
@dataclass
class Account:
    id: int
    user_data: dict

@dataclass
class Transfer:
    from_account: int
    to_account: int
    amount: int

class TigerBeetleClient:
    def __init__(self, host='localhost', port=3000, timeout=5):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None

    def connect(self):
        """Connect to the TigerBeetle server."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.timeout)  # Set a timeout for blocking socket operations
        try:
            self.socket.connect((self.host, self.port))
            print(f"Connected to TigerBeetle server at {self.host}:{self.port}")
        except socket.error as e:
            print(f"Connection error: {e}")
            raise

    def send_message(self, opcode, payload_bytes):
        """Send a message to the server."""
        try:
            # Compute the message size including the header
            message_size = HEADER_SIZE + len(payload_bytes)
            
            # Pack the header (message_size, opcode, result, flags)
            header = struct.pack(HEADER_FORMAT, message_size, opcode, 0, 0)
            
            # Combine the header and payload
            message = header + payload_bytes
            
            # Send the full message to the server
            self.socket.sendall(message)
        except socket.error as e:
            print(f"Send message error: {e}")
            raise

    def receive_response(self):
        """Receive a response from the server."""
        try:
            # Read the header first
            header_bytes = self.socket.recv(HEADER_SIZE)
            if not header_bytes:
                return None
            
            # Unpack the header to get the message size
            message_size, opcode, result, flags = struct.unpack(HEADER_FORMAT, header_bytes)
            
            # Read the rest of the message based on the message size
            response_bytes = self.socket.recv(message_size - HEADER_SIZE)
            
            # Return the opcode and the payload
            return opcode, response_bytes
        except socket.error as e:
            print(f"Receive response error: {e}")
            raise

    def create_accounts(self, accounts):
        """Create new accounts on the server."""
        # Serialize accounts to binary format
        payload_bytes = b''.join(
            struct.pack('>QI', account.id, len(account.user_data)) + account.user_data.encode('utf-8')
            for account in accounts
        )
        self.send_message(OP_CREATE_ACCOUNTS, payload_bytes)
        return self.receive_response()

    def create_transfers(self, transfers):
        """Create new transfers on the server."""
        # Serialize transfers to binary format
        payload_bytes = b''.join(
            struct.pack('>QII', transfer.from_account, transfer.to_account, transfer.amount)
            for transfer in transfers
        )
        self.send_message(OP_CREATE_TRANSFERS, payload_bytes)
        return self.receive_response()

    def close(self):
        """Close the connection to the server."""
        if self.socket:
            self.socket.close()
            self.socket = None

# Example usage
if __name__ == "__main__":
    client = TigerBeetleClient(host='127.0.0.1', port=3000)
    try:
        client.connect()
        
        # Create accounts
        accounts = [
            Account(id=1, user_data='{"name": "John Doe"}'),
            Account(id=2, user_data='{"name": "Jane Doe"}')
        ]
        response = client.create_accounts(accounts)
        print(f"Create Accounts Response: {response}")
        
        # Create transfers
        transfers = [
            Transfer(from_account=1, to_account=2, amount=500)
        ]
        response = client.create_transfers(transfers)
        print(f"Create Transfers Response: {response}")
    finally:
        client.close()
