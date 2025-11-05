# bft/node.py

from blockchain.blockchain import Blockchain
from blockchain.block import Block
import time

class Node:
    def __init__(self, node_id, is_primary=False):
        self.node_id = node_id
        self.blockchain = Blockchain()
        self.is_primary = is_primary
        self.view = 0
        self.prepare_messages = {}
        self.commit_messages = {}
        self.pending_block = None

    def create_block(self, votes):
        """Creates a new block with the given votes."""
        last_block = self.blockchain.last_block
        new_block = Block(
            index=last_block.index + 1,
            transactions=[vote.to_dict() for vote in votes],
            timestamp=time.time(),
            previous_hash=last_block.hash,
        )
        return new_block

    def handle_pre_prepare(self, message):
        """Handles a PRE-PREPARE message from the primary node."""
        print(f"Node {self.node_id}: Received PRE-PREPARE")
        # In a real implementation, validate the message and block
        self.pending_block = message['block']
        # Broadcast a PREPARE message
        return {"status": "PREPARED"}


    def handle_prepare(self, message):
        """Handles a PREPARE message."""
        print(f"Node {self.node_id}: Received PREPARE from {message['sender_id']}")
        block_hash = message['block']['hash']
        if block_hash not in self.prepare_messages:
            self.prepare_messages[block_hash] = []
        self.prepare_messages[block_hash].append(message['sender_id'])

        # Check if we have enough PREPARE messages
        if len(self.prepare_messages.get(block_hash, [])) >= 2 * FAULTY_NODES:
             # Broadcast a COMMIT message
            print(f"Node {self.node_id}: Reached prepared state for block {block_hash}")
            return {"status": "COMMITTED"}
        return {"status": "WAITING_FOR_PREPARES"}


    def handle_commit(self, message):
        """Handles a COMMIT message."""
        print(f"Node {self.node_id}: Received COMMIT from {message['sender_id']}")
        block_hash = message['block']['hash']
        if block_hash not in self.commit_messages:
            self.commit_messages[block_hash] = []
        self.commit_messages[block_hash].append(message['sender_id'])

        # Check if we have enough COMMIT messages
        if len(self.commit_messages.get(block_hash, [])) >= 2 * FAULTY_NODES + 1:
            print(f"Node {self.node_id}: Reached committed state for block {block_hash}")
            # Add the block to the blockchain
            # In a real system, you'd reconstruct the block from the hash or have it stored
            # self.blockchain.add_block(self.pending_block)
            self.pending_block = None
            self.prepare_messages.pop(block_hash, None)
            self.commit_messages.pop(block_hash, None)
            return {"status": "BLOCK_ADDED"}
        return {"status": "WAITING_FOR_COMMITS"}

from config import FAULTY_NODES
