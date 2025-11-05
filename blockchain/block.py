# blockchain/block.py

import time
from utils.cryptography import hash_data

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.compute_hash()

    def compute_hash(self):
        """Computes the hash of the block."""
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hash_data(block_string)
