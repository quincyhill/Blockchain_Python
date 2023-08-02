from flask import Flask, request
from uuid import uuid4
import hashlib
from time import time
from typing import Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class Transaction:
    """
    Just the transaction
    """

    sender: str
    recipient: str
    amount: float


@dataclass(frozen=True)
class Block:
    """
    The block on the blockchain
    """

    index: int
    timestamp: float
    transactions: list[Transaction]
    proof: int
    previous_hash: Optional[str]


class Blockchain:
    def __init__(self) -> None:
        self.chain: list[Block] = []
        self.current_transactions: list[Transaction] = []

    def genesis_block(self) -> Block:
        """
        Creates the Genesis Block
        :return : <dict> New Block
        """
        block = Block(
            index=1,
            timestamp=time(),
            transactions=self.current_transactions,
            proof=0,
            previous_hash=None,
        )

        # Append block to chain array
        self.chain.append(block)

        # return block to be used in the chain
        return block

    def new_block(self, proof: int, previous_hash: str = None) -> Block:
        """
        Create a new Block in the Blockchain
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of the previous Block
        :return : <dict> New Block
        """

        # old_block = { "index": len(self.chain) + 1, "timestamp": time(), "transactions": self.current_transactions, "proof": proof, "previous_hash": previous_hash or self.hash(self.chain[-1])}

        block = Block(
            index=len(self.chain) + 1,
            timestamp=time(),
            transactions=self.current_transactions,
            proof=proof,
            previous_hash=previous_hash or self.hash(self.chain[-1]),
        )

        # Reset the current list of transactions
        self.current_transactions = []

        # Append block to chain array
        self.chain.append(block)

        return block

    def new_transaction(self, sender: str, recipient: str, amount: float) -> int:
        """
        Creates a new transaction to got into the next mined Block
        :param sender: <str> Address of sender
        :param recipient: <str> Address of the Recipient
        :param amount: <float> Amount
        :return : <int> The index of the Block that will hold this transaction
        """
        transaction = Transaction(sender=sender, recipient=recipient, amount=amount)
        self.current_transactions.append(transaction)

        return self.last_block.index + 1

    def proof_of_work(self, last_proof: int) -> int:
        """
        Simple Proof of Work Algorithm:
        - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
        - p is the previous proof, and p' is the new proof
        :param last_proof: <int>
        :return : <int> The new proof
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @property
    def last_block(self) -> Block:
        # :return : <Block> The last block in the chain
        return self.chain[-1]

    @staticmethod
    def hash(block: Block) -> str:
        """
        Create a SHA-256 hash of a Block
        :param block: <dict> Block
        :return : <str>
        """

        # use dataclass info for hashing
        block_string = bytes(str(block), encoding="utf8")
        print("block string", block_string)
        return hashlib.sha256(block_string).hexdigest()

    @staticmethod
    def valid_proof(last_proof: int, proof: int) -> bool:
        """
        Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeros?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return :<bool> True if correct, False if not.
        """
        guess = f"{last_proof}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


# Instantiate out Node
app = Flask(__name__)

# Generate a globally unique address for this node
# will check what that ensures
node_identifier = str(uuid4()).replace("-", "")

# Create the Blockchain instance
blockchain = Blockchain()


@app.route("/", methods=["GET"])
def home():
    # Ignore this its just to test the web server
    return {"hello": "there"}, 200


@app.route("/mine", methods=["GET"])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = None
    if len(blockchain.chain):
        last_block = blockchain.last_block
    else:
        # Create the genisis block here
        last_block = blockchain.genesis_block()

    last_proof = last_block.proof
    proof = blockchain.proof_of_work(last_proof)

    # this is just logging stuff
    print("proof: ", proof)
    print("block chain obj: ", blockchain)

    # The sender is "0" to signify that this node has mined a new coin

    # this will need to be refactored to allow different users to mine
    blockchain.new_transaction(sender="0", recipient=node_identifier, amount=1.00)
    print("new transaction added")

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    print("block has been hashed")
    block = blockchain.new_block(proof, previous_hash)

    print("block: ", block)

    # Don't know why its not printed in order but it works!
    message = {
        "message": "New Block Forged",
        "index": block.index,
        "transactions": block.transactions,
        "proof": block.proof,
        "previous_hash": block.previous_hash,
    }
    return message, 200


# Take note of this post request
@app.route("/transactions/new", methods=["POST"])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ["sender", "recipient", "amount"]
    if not all(k in values for k in required):
        return "Missing values", 400

    # Create a new Transaction
    index = blockchain.new_transaction(
        values["sender"], values["recipient"], values["amount"]
    )

    message = {"message": f"Transaction will be added to Block {index}"}
    return message, 201


@app.route("/chain", methods=["GET"])
def full_chain():
    """
    response = {
            "chain", blockchain.chain,
            "length", len(blockchain.chain),
            }
    return jsonify(response), 200
    """

    thingy = {"chain": blockchain.chain, "length": len(blockchain.chain)}
    return thingy, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
