# Project: Byzantine Fault Tolerance in Blockchain Voting

This document provides the complete file structure and Python code for a distributed computing mini-project demonstrating Byzantine Fault Tolerance (BFT) in a blockchain-based voting system. The implementation uses a simplified version of the Practical Byzantine Fault Tolerance (PBFT) consensus algorithm to ensure the voting process remains secure and reliable, even if some network nodes are faulty or malicious.

The system is designed to tolerate up to `f = (n-1)/3` faulty nodes, where `n` is the total number of nodes in the network, a fundamental property of PBFT.

---

## File Structure

A well-organized file structure is crucial for managing the project's complexity. This structure separates the core logic of the blockchain, the BFT consensus mechanism, the voting application, and utility functions.

```bft-blockchain-voting/
├── blockchain/
│   ├── __init__.py
│   ├── block.py
│   └── blockchain.py
├── bft/
│   ├── __init__.py
│   ├── message.py
│   └── node.py
├── voting/
│   ├── __init__.py
│   ├── api.py
│   └── vote.py
├── utils/
│   ├── __init__.py
│   └── cryptography.py
├── config.py
├── main.py
├── README.md
└── requirements.txt
```

---

## Code Implementation

Below is the Python code for each file in the proposed structure.

### `requirements.txt`

This file lists the necessary Python libraries for the project.

```
Flask==2.2.2
requests==2.28.1
pycryptodome==3.15.0
```

### `config.py`

This file contains configuration settings for the network, such as the total number of nodes, the maximum number of faulty nodes, and their addresses.

```python
# config.py

# Total number of nodes in the network
NUMBER_OF_NODES = 4

# Maximum number of faulty nodes the system can tolerate
# f = (n-1)/3
FAULTY_NODES = int((NUMBER_OF_NODES - 1) / 3)

# Dictionary of node addresses
NODE_ADDRESSES = {i: f"http://127.0.0.1:{5000 + i}" for i in range(NUMBER_OF_NODES)}
```

### `utils/cryptography.py`

This utility file handles cryptographic operations like hashing and digital signatures, which are fundamental to the security of the blockchain.

```python
# utils/cryptography.py

import hashlib
import json
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

def hash_data(data):
    """Hashes the given data using SHA256."""
    if not isinstance(data, str):
        data = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data.encode()).hexdigest()

def generate_keys():
    """Generates a new RSA key pair."""
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

def sign_message(message, private_key_str):
    """Signs a message with a private key."""
    private_key = RSA.import_key(private_key_str)
    if not isinstance(message, bytes):
        message = str(message).encode('utf-8')
    hashed_message = SHA256.new(message)
    signature = pkcs1_15.new(private_key).sign(hashed_message)
    return signature

def verify_signature(message, signature, public_key_str):
    """Verifies a signature with a public key."""
    public_key = RSA.import_key(public_key_str)
    if not isinstance(message, bytes):
        message = str(message).encode('utf-8')
    hashed_message = SHA256.new(message)
    try:
        pkcs1_15.new(public_key).verify(hashed_message, signature)
        return True
    except (ValueError, TypeError):
        return False
```

### `blockchain/block.py`

This file defines the structure of a single block in the blockchain.

```python
# blockchain/block.py

import time
import json
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
        block_dict = self.__dict__
        block_string = json.dumps(block_dict, sort_keys=True)
        return hash_data(block_string)

    def to_dict(self):
        return self.__dict__
```

### `blockchain/blockchain.py`

This file manages the chain of blocks, including the creation of the genesis block and adding new blocks.

```python
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

    def add_block(self, block_data):
        """Adds a new block to the chain from dictionary data."""
        last_block = self.last_block
        if block_data['previous_hash'] != last_block.hash:
            return None # Or raise an error
        
        block = Block(
            index=block_data['index'],
            transactions=block_data['transactions'],
            timestamp=block_data['timestamp'],
            previous_hash=block_data['previous_hash']
        )
        self.chain.append(block)
        return block```

### `voting/vote.py`

This file defines the structure of a single vote, which acts as a transaction in our system.

```python
# voting/vote.py

import time

class Vote:
    def __init__(self, voter_id, candidate_id):
        self.voter_id = voter_id
        self.candidate_id = candidate_id
        self.timestamp = time.time()

    def to_dict(self):
        return self.__dict__
```

### `bft/message.py`

This file defines the different types of messages used in the PBFT consensus algorithm.

```python
# bft/message.py

class Message:
    def __init__(self, message_type, view, block_data, sender_id):
        self.message_type = message_type
        self.view = view
        self.block_data = block_data
        self.sender_id = sender_id

    def to_dict(self):
        return self.__dict__

class PrePrepareMessage(Message):
    def __init__(self, view, block, sender_id):
        super().__init__("PRE-PREPARE", view, block.to_dict(), sender_id)

class PrepareMessage(Message):
    def __init__(self, view, block_hash, sender_id):
        super().__init__("PREPARE", view, {"hash": block_hash}, sender_id)

class CommitMessage(Message):
    def __init__(self, view, block_hash, sender_id):
        super().__init__("COMMIT", view, {"hash": block_hash}, sender_id)
```

### `bft/node.py`

This is the core of the BFT logic. It represents a node in the distributed network and implements the state machine for the PBFT consensus protocol.

```python
# bft/node.py

from blockchain.blockchain import Blockchain
from blockchain.block import Block
from config import FAULTY_NODES
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
        print(f"Node {self.node_id}: Received PRE-PREPARE from {message['sender_id']}")
        # In a real implementation, you would validate the message and block here.
        self.pending_block = message['block_data']
        return {"status": "PREPARE_BROADCASTED"}

    def handle_prepare(self, message):
        """Handles a PREPARE message from other nodes."""
        sender_id = message['sender_id']
        block_hash = message['block_data']['hash']
        print(f"Node {self.node_id}: Received PREPARE from {sender_id} for hash {block_hash[:6]}...")
        
        if block_hash not in self.prepare_messages:
            self.prepare_messages[block_hash] = set()
        self.prepare_messages[block_hash].add(sender_id)

        # Check if we have enough PREPARE messages (2f)
        if len(self.prepare_messages.get(block_hash, set())) >= 2 * FAULTY_NODES:
            print(f"Node {self.node_id}: Reached prepared state for block {block_hash[:6]}...")
            return {"status": "COMMIT_BROADCASTED"}
        return {"status": "WAITING_FOR_MORE_PREPARES"}

    def handle_commit(self, message):
        """Handles a COMMIT message."""
        sender_id = message['sender_id']
        block_hash = message['block_data']['hash']
        print(f"Node {self.node_id}: Received COMMIT from {sender_id} for hash {block_hash[:6]}...")
        
        if block_hash not in self.commit_messages:
            self.commit_messages[block_hash] = set()
        self.commit_messages[block_hash].add(sender_id)

        # Check if we have enough COMMIT messages (2f+1)
        if len(self.commit_messages.get(block_hash, set())) >= 2 * FAULTY_NODES + 1:
            print(f"Node {self.node_id}: Reached committed state for block {block_hash[:6]}...")
            
            # Add the block to the blockchain
            if self.pending_block and self.pending_block['hash'] == block_hash:
                self.blockchain.add_block(self.pending_block)
                print(f"Node {self.node_id}: Successfully added Block {self.pending_block['index']} to the chain.")
                self._reset_state(block_hash)
                return {"status": "BLOCK_ADDED"}
        return {"status": "WAITING_FOR_MORE_COMMITS"}

    def _reset_state(self, block_hash):
        """Resets the state for the next consensus round."""
        self.pending_block = None
        self.prepare_messages.pop(block_hash, None)
        self.commit_messages.pop(block_hash, None)
```

### `voting/api.py`

This file provides a simple Flask API to interact with the voting system. Each node runs its own instance of this API.

```python
# voting/api.py

from flask import Flask, request, jsonify
from bft.node import Node
from voting.vote import Vote
from bft.message import PrePrepareMessage, PrepareMessage, CommitMessage
from config import NODE_ADDRESSES
import requests

app = Flask(__name__)
node = None
votes_to_process = []

def broadcast(endpoint, message):
    """Broadcasts a message to all other nodes."""
    for node_id, address in NODE_ADDRESSES.items():
        if node_id != node.node_id:
            try:
                requests.post(f"{address}/{endpoint}", json=message.to_dict(), timeout=0.5)
            except requests.exceptions.ConnectionError:
                print(f"Node {node.node_id}: Could not connect to Node {node_id}")
            except requests.exceptions.Timeout:
                print(f"Node {node.node_id}: Timeout connecting to Node {node_id}")


@app.route('/vote', methods=['POST'])
def cast_vote():
    """Endpoint for a user to cast a vote."""
    values = request.get_json()
    if not all(key in values for key in ['voter_id', 'candidate_id']):
        return 'Missing values', 400

    vote = Vote(values['voter_id'], values['candidate_id'])
    
    # In a real system, the vote would be sent to the primary. Here we simplify.
    if not node.is_primary:
        return jsonify({'message': 'Please send votes to the primary node (Node 0).'}), 400

    votes_to_process.append(vote)
    print(f"Node {node.node_id} (Primary): Received vote for {values['candidate_id']}. Total pending: {len(votes_to_process)}")

    # Propose a block after collecting 2 votes
    if len(votes_to_process) >= 2:
        propose_block()

    return jsonify({'message': 'Vote received by primary and will be processed.'}), 201

def propose_block():
    """Primary node creates a block and starts the consensus process."""
    global votes_to_process
    if not node.is_primary or not votes_to_process:
        return
        
    new_block = node.create_block(votes_to_process)
    node.pending_block = new_block.to_dict() # Store the block while consensus is in progress
    votes_to_process = [] # Clear the pending votes

    print(f"\nNode {node.node_id} (Primary): Proposing Block {new_block.index} with hash {new_block.hash[:6]}...")
    
    # Broadcast pre-prepare message
    pre_prepare_message = PrePrepareMessage(node.view, new_block, node.node_id)
    broadcast('pre-prepare', pre_prepare_message)


@app.route('/pre-prepare', methods=['POST'])
def pre_prepare():
    message = request.get_json()
    response = node.handle_pre_prepare(message)
    if response['status'] == "PREPARE_BROADCASTED":
        block_hash = message['block_data']['hash']
        prepare_message = PrepareMessage(node.view, block_hash, node.node_id)
        broadcast('prepare', prepare_message)
    return jsonify(response), 200

@app.route('/prepare', methods=['POST'])
def prepare():
    message = request.get_json()
    response = node.handle_prepare(message)
    if response['status'] == "COMMIT_BROADCASTED":
        block_hash = message['block_data']['hash']
        commit_message = CommitMessage(node.view, block_hash, node.node_id)
        broadcast('commit', commit_message)
    return jsonify(response), 200

@app.route('/commit', methods=['POST'])
def commit():
    message = request.get_json()
    response = node.handle_commit(message)
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = [block.to_dict() for block in node.blockchain.chain]
    return jsonify({"length": len(chain_data), "chain": chain_data})

def run_app(node_id, is_primary):
    global node
    node = Node(node_id, is_primary)
    port = 5000 + node_id
    print(f"Starting Node {node_id} {'(Primary)' if is_primary else ''} on port {port}...")
    app.run(host='0.0.0.0', port=port)
```

### `main.py`

This is the entry point for starting a node in the distributed voting system.

```python
# main.py

import argparse
from voting.api import run_app

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run a BFT node for the blockchain voting system.")
    parser.add_argument('--id', required=True, type=int, help="The ID of the node (e.g., 0, 1, 2).")
    parser.add_argument('--primary', action='store_true', help="Set this flag to run the node as the primary.")
    args = parser.parse_args()

    run_app(node_id=args.id, is_primary=args.primary)
```

### `README.md`

A README file with instructions on how to set up and run the project.

```markdown
# Byzantine Fault Tolerance in Blockchain Voting

A mini-project demonstrating Byzantine Fault Tolerance in a blockchain-based voting system using Python and a simplified Practical Byzantine Fault Tolerance (PBFT) consensus algorithm.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd bft-blockchain-voting
    ```

2.  **Install dependencies:**
    It's recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

## Running the System

You need to open multiple terminal windows—one for each node defined by `NUMBER_OF_NODES` in `config.py` (default is 4).

**Terminal 1: Start the Primary Node**

The primary node is responsible for proposing new blocks.

```bash
python main.py --id 0 --primary
```

**Terminal 2: Start Backup Node 1**

```bash
python main.py --id 1
```

**Terminal 3: Start Backup Node 2**

```bash
python main.py --id 2
```

**Terminal 4: Start Backup Node 3**

```bash
python main.py --id 3
```

You should now have four nodes running and listening on ports 5000, 5001, 5002, and 5003.

## Interacting with the System

### 1. Cast Votes

To start the consensus process, you need to send votes to the primary node's `/vote` endpoint. The primary will collect votes and propose a new block once it has enough (currently set to 2).

Open a new terminal to send the requests.

**Cast Vote 1:**```bash
curl -X POST -H "Content-Type: application/json" -d '{
 "voter_id": "VOTER_001",
 "candidate_id": "CANDIDATE_A"
}' http://127.0.0.1:5000/vote
```

**Cast Vote 2:**
```bash
curl -X POST -H "Content-Type: application/json" -d '{
 "voter_id": "VOTER_002",
 "candidate_id": "CANDIDATE_B"
}' http://127.0.0.1:5000/vote
```

After the second vote is sent, you will see log messages in all node terminals as they go through the `PRE-PREPARE`, `PREPARE`, and `COMMIT` phases of the PBFT algorithm.

### 2. View the Blockchain

To verify that the new block has been added consistently across all nodes, you can check the blockchain state of each node.

**Check Node 0's chain:**
```bash
curl http://127.0.0.1:5000/chain
```

**Check Node 1's chain:**
```bash
curl http://127.0.0.1:5001/chain
```

All nodes should show an identical blockchain with the newly added block containing the two votes.
```
