#!/home/rob/py_36/bin/python3.6

import sys
import os
import json
import web3
from web3 import Web3
from termcolor import colored
from computable.helpers.transaction import send
from computable.contracts import EtherToken

PROVIDER_URI = 'http://mainnet.computablelabs.com:8545'
# TODO could use a config file and fetch...
GAS_PRICE = None
PUBLIC_KEY = os.environ.get('public_key')
PRIVATE_KEY = os.environ.get('private_key')

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

def deploy_ether_token(w3):
    abi = None
    bc = None
    with open('ethertoken/ethertoken.abi') as f:
        abi = json.loads(f.read())
    with open('ethertoken/ethertoken.bin') as f:
        bc = f.read()
    if abi is None:
        print(colored('Error reading Ether Token ABI', 'red'))
        sys.exit(1)
    if bc is None:
        print(colored('Error reading Ether Token Bytecode', 'red'))
        sys.exit(1)
    deployed = w3.eth.contract(abi=abi, bytecode=bc.rstrip('\n'))

    # build the args for the send method
    args = get_deployment_args(w3, deployed.constructor())
    # use computable.py's ability to sign offline
    tx_hash = send(w3, PRIVATE_KEY, args)
    # wait for it... TODO adjust timeout
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

    print(colored(heading('Gas Price check'), 'yellow'))
    if not GAS_PRICE:
        sys.exit(1)
    print('Gas Price available. Continuing...')

    print(colored(heading('Deploying Ether Token'), 'yellow'))
    ether_token_address = deploy_ether_token(w3)
    print(colored(ether_token_address, 'green'))
