#!/home/rob/py_36/bin/python3.6

import sys
import os
import web3
from web3 import Web3
from termcolor import colored
from computable.helpers.transaction import call, send
from computable.contracts import Datatrust

PROVIDER_URI = 'http://mainnet.computablelabs.com:8545'
GAS_PRICE = None
PUBLIC_KEY = os.environ.get('public_key')
PRIVATE_KEY = os.environ.get('private_key')
DATATRUST_ADDRESS = None
LISTING_ADDRESS = None

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

    print(colored(heading('Datatrust Address check'), 'yellow'))
    if not DATATRUST_ADDRESS:
        sys.exit(1)
    print('Datatrust Address available. Continuing...')

    print(colored(heading('Listing Address check'), 'yellow'))
    if not LISTING_ADDRESS:
        sys.exit(1)
    print('Listing Address available. Continuing...')

    print(colored(heading('Set Datatrust privileged'), 'yellow'))
    print(colored('instantiating Datatrust', 'blue'))
    datatrust = Datatrust(PUBLIC_KEY)
    datatrust.at(w3, DATATRUST_ADDRESS)
    print(colored('Setting addresses...', 'blue'))
    d_gas = datatrust.deployed.functions.setPrivileged(LISTING_ADDRESS).estimateGas()
    d_args = datatrust.set_privileged(LISTING_ADDRESS, {'gas': d_gas, 'gas_price': w3.toWei(GAS_PRICE, 'gwei')})
    d_tx_hash = send(w3, PRIVATE_KEY, d_args)
    d_tx_rct = w3.eth.waitForTransactionReceipt(d_tx_hash)
    print(colored(d_tx_rct, 'green'))
