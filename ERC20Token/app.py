import os
import json
import argparse

from dotenv import load_dotenv
from urllib.request import urlopen
from web3 import Web3


load_dotenv()  # take environment variables from .env.

# The scope below mostly use the uniswap python API in order to easily check some informations

DAPP_URL=os.getenv('DAPP_URL')

token_addresses = {
    # An error may occured if you get addresses that are not checksumed (usually when using external tools).
    "weth": Web3.toChecksumAddress("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
    "uni": Web3.toChecksumAddress("0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"),
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

UNISWAP_ROUTER_ADDRESS=os.getenv('UNISWAP_ROUTER_ADDRESS')
UNISWAP_ROUTER_ABI_URL=os.getenv('UNISWAP_ROUTER_ABI_URL')
UNISWAP_ROUTER_ABI=_read_remote_abi(UNISWAP_ROUTER_ABI_URL)


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

    return (uniswap_pair_contract, token_0_contract, token_1_contract)


def get_token_price_from_router(w3_provider, amount_in, uniswap_pair_contract):
    router_contract = w3_provider.eth.contract(address=UNISWAP_ROUTER_ADDRESS, abi=UNISWAP_ROUTER_ABI)
    return router_contract.caller().getAmountsOut(
        amount_in,
        [uniswap_pair_contract.caller().token0(), uniswap_pair_contract.caller().token1()]
    )


def get_token_price(amount_in, uniswap_pair_contract):
    # Compute based on getAmountOut() from UniswapV2Library.sol
    #
    # uint amountInWithFee = amountIn.mul(997);
    # uint numerator = amountInWithFee.mul(reserveOut);
    # uint denominator = reserveIn.mul(1000).add(amountInWithFee);
    # amountOut = numerator / denominator;
    #
    (reserve_in, reserve_out, _) = uniswap_pair_contract.caller().getReserves()
    amount_in_with_fee = amount_in * 997
    numerator = amount_in_with_fee * reserve_out
    denominator = reserve_in * 1000 + amount_in_with_fee
    return numerator / denominator


def check_token_price_v2(w3_provider, amount, token_a, token_b="usdt"):
    uniswap_pair_contract = get_pair_contract(w3_provider, token_a, token_b)

    # Use static amount for now
    amount_in = amount*10**18
    rate = 10**6

    # Ceheck price using custom strategy
    return get_token_price(amount_in, uniswap_pair_contract) / rate


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description ='Check price for given amount of token A to token B')

    parser.add_argument('--token-a', required=True, type=str, help='token A symbol')
    parser.add_argument('--token-b', required=True, type=str, help='token B symbol')
    parser.add_argument('--amount', required=True, type=int, help='token B symbol')

    args = parser.parse_args()

    w3 = Web3(Web3.HTTPProvider(DAPP_URL))
    if not w3.isConnected():
        raise RuntimeError("Failed to connect to web3 provider")

    if not "usdt" in [args.token_a, args.token_b]:
        price_a = check_token_price_v2(w3, 1, args.token_a)
        price_b = check_token_price_v2(w3, 1, args.token_b)
        price = price_a / price_b
    else:
        price = check_token_price_v2(w3, args.amount, args.token_a.lower(), args.token_b.lower())

    print(f"{args.amount} {args.token_a} -> {price} {args.token_b}")