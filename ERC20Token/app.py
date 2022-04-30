import os
import json

from dotenv import load_dotenv
from urllib.request import urlopen
from web3 import Web3


load_dotenv()  # take environment variables from .env.

# The scope below mostly use the uniswap python API in order to easily check some informations

DAPP_URL=os.getenv('DAPP_URL')

token_addresses = {
    # An error may occured if you get addresses that are not checksumed (usually when using external tools).
    "weth": Web3.toChecksumAddress("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
    "usdt": Web3.toChecksumAddress("0xdAC17F958D2ee523a2206206994597C13D831ec7"),
}

def check_token_price(token):
    # using late import to limit the import to this function
    from uniswap import Uniswap
    uniswap = Uniswap(address=None, private_key=None, version=2, provider=DAPP_URL)
    print(uniswap.get_token(token_addresses[token]))
    print(uniswap.get_token(token_addresses["usdt"]))
    return uniswap.get_price_input(token_addresses[token], token_addresses["usdt"], 10**18)


# The scope below focus on using the uniswap contract directly

def _read_remote_abi(abi_url):
    response = urlopen(abi_url)
    response_content = response.read()
    json_content = json.loads(response_content)
    return json_content["abi"]


UNISWAP_FACTORY_ADDRESS=os.getenv("UNISWAP_FACTORY_ADDRESS")
UNISWAP_FACTORY_ABI_URL=os.getenv('UNISWAP_FACTORY_ABI_URL')
UNISWAP_FACTORY_ABI=_read_remote_abi(UNISWAP_FACTORY_ABI_URL)

UNISWAP_PAIR_ABI_URL=os.getenv('UNISWAP_PAIR_ABI_URL')
UNISWAP_PAIR_ABI=_read_remote_abi(UNISWAP_PAIR_ABI_URL)

UNISWAP_PAIR_ABI_URL=os.getenv('UNISWAP_PAIR_ABI_URL')
UNISWAP_PAIR_ABI=_read_remote_abi(UNISWAP_PAIR_ABI_URL)


def get_pair_contract(w3_provider, token_a, token_b):
    # get uniswap factory contract
    uniswap_factory = w3_provider.eth.contract(address=UNISWAP_FACTORY_ADDRESS, abi=UNISWAP_FACTORY_ABI)
    if uniswap_factory is None:
        raise RuntimeError("Failed to get Uniswap factory contract")

    # get the contract address for the given pair [token, "usdt"]
    pair_address = uniswap_factory.caller().getPair(token_addresses[token_a], token_addresses[token_b])
    if pair_address is None:
        raise RuntimeError(f"Failed to get pair contract address for pair [{token_a}, {token_b}]")

    # get the uniswap pair contract for the given pair
    uniswap_pair_contract = w3_provider.eth.contract(address=pair_address, abi=UNISWAP_PAIR_ABI)
    if uniswap_pair_contract is None:
        raise RuntimeError(f"Failed to get pair contract for pair [{token_a}, {token_b}]")

    return uniswap_pair_contract


def get_token_contract_from_pair(w3_provider, token_a, token_b):
    uniswap_pair_contract = get_pair_contract(w3_provider, token_a, token_b)

    # get the UniswapV2ERC20 contract for each token
    token_0_contract_address = uniswap_pair_contract.caller().token0()
    if token_0_contract_address is None:
        raise RuntimeError(f"Failed to get token contract address for token: {token_a}")

    token_0_contract = w3_provider.eth.contract(address=token_0_contract_address, abi=UNISWAP_PAIR_ABI)
    if token_0_contract is None:
        raise RuntimeError(f"Failed to get token contract for token: {token_a}")

    token_1_contract_address = uniswap_pair_contract.caller().token1()
    if token_1_contract_address is None:
        raise RuntimeError(f"Failed to get token contract address for token: {token_b}")

    token_1_contract = w3_provider.eth.contract(address=token_1_contract_address, abi=UNISWAP_PAIR_ABI)
    if token_1_contract is None:
        raise RuntimeError(f"Failed to get token contract for token: {token_b}")

    return (token_0_contract, token_1_contract)


def check_token_price_v2(w3_provider, token_a, token_b="usdt"):
    (token_0_contract, token_1_contract) = get_token_contract_from_pair(w3_provider, token_a, token_b)

    # Check that token symbols match given symbols
    assert(token_0_contract.caller().symbol().lower() == token_a.lower())
    assert(token_1_contract.caller().symbol().lower() == token_b.lower())


if __name__ == "__main__":
    w3 = Web3(Web3.HTTPProvider(DAPP_URL))
    print(w3.isConnected())
    check_token_price_v2(w3, "weth")