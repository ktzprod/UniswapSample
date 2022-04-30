from lib2to3.pgen2 import token
import os

from ERC20Token.app import get_pair_contract, get_token_contract_from_pair, get_token_price
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()  # take environment variables from .env.
DAPP_URL=os.getenv('DAPP_URL')
w3 = Web3(Web3.HTTPProvider(DAPP_URL))
assert(w3.isConnected())

pair_to_test = [
    ("weth", "usdt"),
    ("weth", "uni"),
    ("uni", "usdt"),
]

def test_get_pair_contract():
    for pair in pair_to_test:
        (a, b) = pair
        assert get_pair_contract(w3, a, b) is not None


def test_get_token_contract_from_pair():
    for pair in pair_to_test:
        (a, b) = pair
        (_, token_a, token_b) = get_token_contract_from_pair(w3, a, b)
        assert token_a.caller().symbol().lower() in pair
        assert token_b.caller().symbol().lower() in pair

