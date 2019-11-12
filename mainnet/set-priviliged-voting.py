#!/home/rob/py_36/bin/python3.6

import sys
import os
import web3
from web3 import Web3
from termcolor import colored
from computable.helpers.transaction import call, send
from computable.contracts import Voting

PROVIDER_URI = 'http://mainnet.computablelabs.com:8545'
GAS_PRICE = None
PUBLIC_KEY = os.environ.get('public_key')
PRIVATE_KEY = os.environ.get('private_key')
PARAMETERIZER_ADDRESS = None
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

    print(colored(heading('Parameterizer Address check'), 'yellow'))
    if not PARAMETERIZER_ADDRESS:
        sys.exit(1)
    print('Parameterizer Address available. Continuing...')

    print(colored(heading('Datatrust Address check'), 'yellow'))
    if not DATATRUST_ADDRESS:
        sys.exit(1)
    print('Datatrust Address available. Continuing...')

    print(colored(heading('Listing Address check'), 'yellow'))
    if not LISTING_ADDRESS:
        sys.exit(1)
    print('Listing Address available. Continuing...')

    print(colored(heading('Set Voting privileged'), 'yellow'))
    print(colored('instantiating Voting', 'blue'))
    voting = Voting(PUBLIC_KEY)
    voting.at(w3, VOTING_ADDRESS)
    print(colored('Setting addresses...', 'blue'))
    v_gas = voting.deployed.functions.setPrivileged(PARAMETERIZER_ADDRESS, DATATRUST_ADDRESS, LISTING_ADDRESS).estimateGas()
    v_args = voting.set_privileged(PARAMETERIZER_ADDRESS, DATATRUST_ADDRESS, LISTING_ADDRESS, {'gas': v_gas, 'gas_price': w3.toWei(GAS_PRICE, 'gwei')})
    v_tx_hash = send(w3, PRIVATE_KEY, v_args)
    v_tx_rct = w3.eth.waitForTransactionReceipt(v_tx_hash)
    print(colored(v_tx_rct, 'green'))
