# UniswapSample
Small python sample onhow to interact with UniswapV2 API

# Usage

The sample can be called using the mandatory arguments:
- token-a: the input token
- token-b: the output token
- amount: the amount of token A for conversion

Exemple:

```python .\ERC20Token\app.py --token-a weth --token-b usdt --amount 30```

# Environment

Your .env file need to specify:

- DAPP_URL - meaning the URL for the HTTP provider 
- UNISWAP_FACTORY_ABI_URL - the uniswap factory ABI
- UNISWAP_FACTORY_ADDRESS - the uniswap factory contract address
- UNISWAP_PAIR_ABI_URL - the uniswap pair ABI
- UNISWAP_ERC20_TOKEN_ABI_URL - the uniswap pair(ERC20) contract address
- UNISWAP_ROUTER_ADDRESS - the uniswap router address
- UNISWAP_ROUTER_ABI_URL - the uniswap router ABI