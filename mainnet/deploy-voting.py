#!/home/rob/py_36/bin/python3.6

import sys
import os
import json
import web3
from web3 import Web3
from termcolor import colored
from computable.helpers.transaction import send
from computable.contracts import Voting

PROVIDER_URI = 'http://mainnet.computablelabs.com:8545'
GAS_PRICE = None
PUBLIC_KEY = os.environ.get('public_key')
PRIVATE_KEY = os.environ.get('private_key')
# TODO could be fetched from the info file via filereader
MARKET_TOKEN_ADDRESS = None

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

def deploy_voting(w3):
    abi = None
    bc = None
    with open('voting/voting.abi') as f:
        abi = json.loads(f.read())
    with open('voting/voting.bin') as f:
        bc = f.read()
    if abi is None:
        print(colored('Error reading Voting ABI', 'red'))
        sys.exit(1)
    if bc is None:
        print(colored('Error reading Voting Bytecode', 'red'))
        sys.exit(1)
    deployed = w3.eth.contract(abi=abi, bytecode=bc.rstrip('\n'))
    args = get_deployment_args(w3, deployed.constructor(MARKET_TOKEN_ADDRESS))
    tx_hash = send(w3, PRIVATE_KEY, args)
    tx_rct = w3.eth.waitForTransactionReceipt(tx_hash)
    return tx_rct['contractAddress']

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

    print(colored(heading('Gas Price check'), 'yellow'))
    if not GAS_PRICE:
        sys.exit(1)
    print('Gas Price available. Continuing...')

    print(colored(heading('Deploying Voting'), 'yellow'))
    voting_address = deploy_voting(w3)
    print(colored(voting_address, 'green'))
