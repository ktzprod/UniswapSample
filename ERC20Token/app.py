import os

from dotenv import load_dotenv
from web3 import Web3

load_dotenv()  # take environment variables from .env.

DAPP_URL=os.getenv('DAPP_URL')


if __name__ == "__main__":
    w3 = Web3(Web3.HTTPProvider(DAPP_URL))
    print(w3.isConnected())