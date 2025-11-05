# blockchain/blockchain.py

from blockchain.block import Block
import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        """Creates the very first block in the chain."""
        genesis_block = Block(0, [], time.time(), "0")
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        """Returns the most recent block in the chain."""
        return self.chain[-1]

    def add_block(self, block):
        """Adds a new block to the chain."""
        # In a real application, you would have proof-of-work or other validation here
        self.chain.append(block)
        return block
