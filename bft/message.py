# bft/message.py

class Message:
    """
    Base class for all messages exchanged during the consensus process.
    """
    def __init__(self, message_type, view, block_data, sender_id):
        self.message_type = message_type
        self.view = view
        self.block_data = block_data
        self.sender_id = sender_id

    def to_dict(self):
        """Converts the message object to a dictionary for JSON serialization."""
        return self.__dict__

class PrePrepareMessage(Message):
    """
    A PRE-PREPARE message, sent by the primary node to initiate consensus.
    It contains the full proposed block.
    """
    def __init__(self, view, block, sender_id):
        super().__init__("PRE-PREPARE", view, block.to_dict(), sender_id)

class PrepareMessage(Message):
    """
    A PREPARE message, broadcast by backup nodes after receiving a valid PRE-PREPARE.
    It contains the hash of the proposed block.
    """
    def __init__(self, view, block_hash, sender_id):
        super().__init__("PREPARE", view, {"hash": block_hash}, sender_id)

class CommitMessage(Message):
    """
    A COMMIT message, broadcast by nodes once they have received enough PREPARE messages.
    It signifies agreement on the block and readiness to add it to the chain.
    """
    def __init__(self, view, block_hash, sender_id):
        super().__init__("COMMIT", view, {"hash": block_hash}, sender_id)
