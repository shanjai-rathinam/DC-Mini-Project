# voting/vote.py

import time

class Vote:
    def __init__(self, voter_id, candidate_id):
        self.voter_id = voter_id
        self.candidate_id = candidate_id
        self.timestamp = time.time()

    def to_dict(self):
        return self.__dict__
