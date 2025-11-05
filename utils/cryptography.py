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
