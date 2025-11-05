# config.py

NUMBER_OF_NODES = 4
FAULTY_NODES = 1
NODE_ADDRESSES = {i: f"http://127.0.0.1:{5000 + i}" for i in range(NUMBER_OF_NODES)}
