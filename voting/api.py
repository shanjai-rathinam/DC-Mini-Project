# voting/api.py

from flask import Flask, request, jsonify
from bft.node import Node
from voting.vote import Vote
import requests
from config import NODE_ADDRESSES

app = Flask(__name__)
node = None
votes_to_process = []

@app.route('/vote', methods=['POST'])
def cast_vote():
    values = request.get_json()
    if not all(key in values for key in ['voter_id', 'candidate_id']):
        return 'Missing values', 400

    vote = Vote(values['voter_id'], values['candidate_id'])
    votes_to_process.append(vote)

    # In a real system, the primary node would be determined dynamically.
    if node.is_primary and len(votes_to_process) >= 2: # Create a block after 2 votes
        propose_block()

    return jsonify({'message': 'Vote has been received'}), 201

def propose_block():
    global votes_to_process
    new_block = node.create_block(votes_to_process)
    votes_to_process = []

    # Broadcast pre-prepare message
    for node_id, address in NODE_ADDRESSES.items():
        if node_id != node.node_id:
            try:
                requests.post(f"{address}/pre-prepare", json={
                    "view": node.view,
                    "block": new_block.__dict__,
                    "sender_id": node.node_id
                })
            except requests.exceptions.ConnectionError:
                print(f"Could not connect to Node {node_id}")


@app.route('/pre-prepare', methods=['POST'])
def pre_prepare():
    message = request.get_json()
    response = node.handle_pre_prepare(message)
    if response['status'] == "PREPARED":
        # Broadcast prepare
        block_hash = message['block']['hash']
        for node_id, address in NODE_ADDRESSES.items():
             try:
                requests.post(f"{address}/prepare", json={
                    "view": node.view,
                    "block": {"hash": block_hash},
                    "sender_id": node.node_id
                })
             except requests.exceptions.ConnectionError:
                print(f"Could not connect to Node {node_id}")

    return jsonify(response), 200

@app.route('/prepare', methods=['POST'])
def prepare():
    message = request.get_json()
    response = node.handle_prepare(message)
    if response['status'] == "COMMITTED":
        # Broadcast commit
        block_hash = message['block']['hash']
        for node_id, address in NODE_ADDRESSES.items():
            try:
                requests.post(f"{address}/commit", json={
                    "view": node.view,
                    "block": {"hash": block_hash},
                    "sender_id": node.node_id
                })
            except requests.exceptions.ConnectionError:
                print(f"Could not connect to Node {node_id}")
    return jsonify(response), 200

@app.route('/commit', methods=['POST'])
def commit():
    message = request.get_json()
    response = node.handle_commit(message)
    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in node.blockchain.chain:
        chain_data.append(block.__dict__)
    return jsonify({"length": len(chain_data), "chain": chain_data})


def run_app(node_id, is_primary):
    global node
    node = Node(node_id, is_primary)
    port = 5000 + node_id
    app.run(port=port)
