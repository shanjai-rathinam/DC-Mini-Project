# main.py

import argparse
from voting.api import run_app

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run a BFT node.")
    parser.add_argument('--id', required=True, type=int, help="The ID of the node.")
    parser.add_argument('--primary', action='store_true', help="Set this node as the primary.")
    args = parser.parse_args()

    run_app(args.id, args.primary)
