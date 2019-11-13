#!~/compas_env/bin/python3.6

import sys
import os
import web3
from web3 import Web3
from termcolor import colored
from computable.helpers.transaction import call, send
from computable.contracts import MarketToken

PROVIDER_URI = 'http://mainnet.computablelabs.com:8545'
GAS_PRICE = 10
PUBLIC_KEY = os.environ.get('public_key')
PRIVATE_KEY = os.environ.get('private_key')
MARKET_TOKEN_ADDRESS = '0x4BbD0678d0ff2e289506152F4B53090E2f9Dc4D0'
RESERVE_ADDRESS = '0x2c5358c9573ad83cEb510982a438edcd5b0e0a81'
LISTING_ADDRESS = '0x4587AaC1285cDa2ea573de911992d44A1c4C3A54'

def heading(val):
    return f'************* {val} *************'

def get_w3():
    provider = web3.HTTPProvider(PROVIDER_URI)
    w3 = Web3(provider)
    w3.eth.defaultAccount = PUBLIC_KEY
    return w3

def get_deployment_args(w3, tx):
    """
    Return a tuple of 2 -> (tx, opts)
    """
    gas = tx.estimateGas()

    return (tx, {'gas': gas, 'gasPrice': w3.toWei(GAS_PRICE, 'gwei'), 'from': PUBLIC_KEY})


if __name__ == '__main__':
    print(colored(heading('Setting up Web3'), 'yellow'))
    w3 = get_w3()
    print(colored(w3.clientVersion, 'green'))

    print(colored(heading('Connecting to node - show latest block'), 'yellow'))
    print(w3.eth.getBlock('latest'))

    print(colored(heading('Default account (public key) check'), 'yellow'))
    if w3.eth.defaultAccount is None:
        sys.exit(1)
    print(w3.eth.defaultAccount)

    print(colored(heading('Private key check'), 'yellow'))
    if not PRIVATE_KEY:
        sys.exit(1)
    print('Private key available. Continuing...')

    print(colored(heading('Market Token Address check'), 'yellow'))
    if not MARKET_TOKEN_ADDRESS:
        sys.exit(1)
    print('Market Token Address available. Continuing...')

    print(colored(heading('Reserve Address check'), 'yellow'))
    if not RESERVE_ADDRESS:
        sys.exit(1)
    print('Reserve Address available. Continuing...')

    print(colored(heading('Listing Address check'), 'yellow'))
    if not LISTING_ADDRESS:
        sys.exit(1)
    print('Listing Address available. Continuing...')

    print(colored(heading('Set Market Token privileged'), 'yellow'))
    print(colored('instantiating MarketToken', 'blue'))
    market_token = MarketToken(PUBLIC_KEY)
    market_token.at(w3, MARKET_TOKEN_ADDRESS)
    print(colored('Setting addresses...', 'blue'))
    mt_gas = market_token.deployed.functions.setPrivileged(RESERVE_ADDRESS, LISTING_ADDRESS).estimateGas()
    mt_args = market_token.set_privileged(RESERVE_ADDRESS, LISTING_ADDRESS, {'gas': mt_gas, 'gas_price': w3.toWei(GAS_PRICE, 'gwei')})
    mt_tx_hash = send(w3, PRIVATE_KEY, mt_args)
    mt_tx_rct = w3.eth.waitForTransactionReceipt(mt_tx_hash)
    print(colored(mt_tx_rct, 'green'))
