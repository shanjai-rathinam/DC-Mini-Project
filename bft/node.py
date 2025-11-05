# bft/node.py

from blockchain.blockchain import Blockchain
from blockchain.block import Block
from config import FAULTY_NODES
import time

class Node:
    """
    Represents a single node (server) in the BFT network.
    """
    def __init__(self, node_id, is_primary=False):
        self.node_id = node_id
        self.blockchain = Blockchain()
        self.is_primary = is_primary
        self.view = 0  # The current view number in the PBFT protocol.
        
        # Dictionaries to store received consensus messages for a given block hash.
        self.prepare_messages = {}
        self.commit_messages = {}
        
        # Stores the block that is currently undergoing the consensus process.
        self.pending_block = None

    def create_block(self, votes):
        """Creates a new block to be proposed."""
        last_block = self.blockchain.last_block
        new_block = Block(
            index=last_block.index + 1,
            transactions=[vote.to_dict() for vote in votes],
            timestamp=time.time(),
            previous_hash=last_block.hash,
        )
        return new_block

    def handle_pre_prepare(self, message):
        """
        Handles an incoming PRE-PREPARE message from the primary node.
        This is the first step of the consensus protocol for backup nodes.
        """
        sender_id = message['sender_id']
        block_hash = message['block_data']['hash']
        print(f"Node {self.node_id}: Received PRE-PREPARE from Node {sender_id} for block hash {block_hash[:6]}...")
        
        # In a real system, extensive validation of the block and message signature would occur here.
        # For this project, we assume the message is valid.
        
        self.pending_block = message['block_data']
        return {"status": "PREPARE_BROADCASTED"}

    def handle_prepare(self, message):
        """
        Handles an incoming PREPARE message. Nodes collect these messages to
        confirm that other nodes also received and validated the PRE-PREPARE.
        """
        sender_id = message['sender_id']
        block_hash = message['block_data']['hash']
        print(f"Node {self.node_id}: Received PREPARE from Node {sender_id} for hash {block_hash[:6]}...")
        
        if block_hash not in self.prepare_messages:
            self.prepare_messages[block_hash] = set()
        self.prepare_messages[block_hash].add(sender_id)

        # Once a node has received 2f matching PREPARE messages from different nodes,
        # it has reached the "prepared" state for this block.
        if len(self.prepare_messages.get(block_hash, set())) >= 2 * FAULTY_NODES:
            print(f"Node {self.node_id}: Reached prepared state for block {block_hash[:6]}...")
            return {"status": "COMMIT_BROADCASTED"}
            
        return {"status": "WAITING_FOR_MORE_PREPARES"}

    def handle_commit(self, message):
        """
        Handles an incoming COMMIT message. Nodes collect these to confirm that
        a sufficient number of nodes have reached the "prepared" state.
        """
        sender_id = message['sender_id']
        block_hash = message['block_data']['hash']
        print(f"Node {self.node_id}: Received COMMIT from Node {sender_id} for hash {block_hash[:6]}...")
        
        if block_hash not in self.commit_messages:
            self.commit_messages[block_hash] = set()
        self.commit_messages[block_hash].add(sender_id)

        # Once a node receives 2f+1 COMMIT messages, it can safely commit
        # the block to its local blockchain. This is the final step.
        if len(self.commit_messages.get(block_hash, set())) >= 2 * FAULTY_NODES + 1:
            print(f"Node {self.node_id}: Reached committed state for block {block_hash[:6]}...")
            
            # Add the block to the local blockchain
            if self.pending_block and self.pending_block['hash'] == block_hash:
                self.blockchain.add_block(self.pending_block)
                print(f"Node {self.node_id}: >>> Successfully added Block {self.pending_block['index']} to the chain. <<<")
                self._reset_state(block_hash)
                return {"status": "BLOCK_ADDED"}
                
        return {"status": "WAITING_FOR_MORE_COMMITS"}

    def _reset_state(self, block_hash):
        """
        Clears the state related to the last consensus round to prepare for the next one.
        """
        print(f"Node {self.node_id}: Resetting state for next consensus round.\n")
        self.pending_block = None
        self.prepare_messages.pop(block_hash, None)
        self.commit_messages.pop(block_hash, None)
