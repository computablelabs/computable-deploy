#!/home/rob/py_36/bin/python3.6

import sys
import os
import json
import web3
from web3 import Web3
from termcolor import colored
from computable.helpers.transaction import send
from computable.contracts import Parameterizer

PROVIDER_URI = 'http://mainnet.computablelabs.com:8545'
GAS_PRICE = None
PUBLIC_KEY = os.environ.get('public_key')
PRIVATE_KEY = os.environ.get('private_key')
MARKET_TOKEN_ADDRESS = None
VOTING_ADDRESS = None

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

def get_parameterizer_opts():
    return {
        'price_floor': Web3.toWei(500, 'kwei'), # 5e5
        'spread': 110,
        'list_reward': Web3.toWei(2, 'ether'), # 2e18
        'stake': Web3.toWei(10, 'ether'), # 1e19
        'vote_by': 3600, # an hour TODO change to seconds in 24 hours -> 86400 when ready
        'plurality': 50,
        'backend_payment': 5,
        'maker_payment': 70,
        'cost_per_byte': Web3.toWei(550, 'mwei') # 5.5e8 -> about 11/mbyte cents atm
        }

def deploy_parameterizer(w3):
    parameterizer_opts = get_parameterizer_opts()
    abi = None
    bc = None
    with open('parameterizer/parameterizer.abi') as f:
        abi = json.loads(f.read())
    with open('parameterizer/parameterizer.bin') as f:
        bc = f.read()
    if abi is None:
        print(colored('Error reading Parameterizer ABI', 'red'))
        sys.exit(1)
    if bc is None:
        print(colored('Error reading Parameterizer Bytecode', 'red'))
        sys.exit(1)
    deployed = w3.eth.contract(abi=abi, bytecode=bc.rstrip('\n'))
    args = get_deployment_args(w3, deployed.constructor(
            MARKET_TOKEN_ADDRESS,
            VOTING_ADDRESS,
            parameterizer_opts['price_floor'],
            parameterizer_opts['spread'],
            parameterizer_opts['list_reward'],
            parameterizer_opts['stake'],
            parameterizer_opts['vote_by'],
            parameterizer_opts['plurality'],
            parameterizer_opts['backend_payment'],
            parameterizer_opts['maker_payment'],
            parameterizer_opts['cost_per_byte']
            ))
    tx_hash = send(w3, PRIVATE_KEY, args)
    tx_rcpt = w3.eth.waitForTransactionReceipt(tx_hash)
    return tx_rcpt['contractAddress']

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

    print(colored(heading('Voting Address check'), 'yellow'))
    if not VOTING_ADDRESS:
        sys.exit(1)
    print('Voting Address available. Continuing...')

    print(colored(heading('Gas Price check'), 'yellow'))
    if not GAS_PRICE:
        sys.exit(1)
    print('Gas Price available. Continuing...')

    print(colored(heading('Deploying Parameterizer'), 'yellow'))
    parameterizer_address = deploy_parameterizer(w3)
    print(colored(parameterizer_address, 'green'))
