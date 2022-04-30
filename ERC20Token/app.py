import os

from dotenv import load_dotenv
from web3 import Web3


load_dotenv()  # take environment variables from .env.

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


if __name__ == "__main__":
    w3 = Web3(Web3.HTTPProvider(DAPP_URL))
    print(w3.isConnected())
    print(check_token_price("weth"))