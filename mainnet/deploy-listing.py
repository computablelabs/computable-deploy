#!~/compas_env/bin/python3.6

import sys
import os
import json
import web3
from web3 import Web3
from termcolor import colored
from computable.helpers.transaction import send
from computable.contracts import Listing

PROVIDER_URI = 'http://mainnet.computablelabs.com:8545'
GAS_PRICE = 10
PUBLIC_KEY = os.environ.get('public_key')
PRIVATE_KEY = os.environ.get('private_key')
MARKET_TOKEN_ADDRESS = '0x4BbD0678d0ff2e289506152F4B53090E2f9Dc4D0'
VOTING_ADDRESS = '0xf3a70Bd65b72065C89625Eb7d9D57cd6487F1982'
PARAMETERIZER_ADDRESS = '0x0EA44154C2FaE1621FbB31CEc4119Cc523B3702a'
RESERVE_ADDRESS = '0x2c5358c9573ad83cEb510982a438edcd5b0e0a81'
DATATRUST_ADDRESS = '0xEd80E4627cEe54b72F406d61A43637E5dFB2e45c'

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

def deploy_listing(w3):
    abi = None
    bc = None
    with open('listing/listing.abi') as f:
        abi = json.loads(f.read())
    with open('listing/listing.bin') as f:
        bc = f.read()
    if abi is None:
        print(colored('Error reading Listing ABI', 'red'))
        sys.exit(1)
    if bc is None:
        print(colored('Error reading Listing Bytecode', 'red'))
        sys.exit(1)
    deployed = w3.eth.contract(abi=abi, bytecode=bc.rstrip('\n'))
    args = get_deployment_args(w3, deployed.constructor(MARKET_TOKEN_ADDRESS, VOTING_ADDRESS, PARAMETERIZER_ADDRESS, RESERVE_ADDRESS, DATATRUST_ADDRESS))
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

    print(colored(heading('Voting Address check'), 'yellow'))
    if not VOTING_ADDRESS:
        sys.exit(1)
    print('Voting Address available. Continuing...')

    print(colored(heading('Parameterizer Address check'), 'yellow'))
    if not PARAMETERIZER_ADDRESS:
        sys.exit(1)
    print('Parameterizer Address available. Continuing...')

    print(colored(heading('Reserve Address check'), 'yellow'))
    if not RESERVE_ADDRESS:
        sys.exit(1)
    print('Reserve Address available. Continuing...')

    print(colored(heading('Datatrust Address check'), 'yellow'))
    if not DATATRUST_ADDRESS:
        sys.exit(1)
    print('Datatrust Address available. Continuing...')

    print(colored(heading('Gas Price check'), 'yellow'))
    if not GAS_PRICE:
        sys.exit(1)
    print('Gas Price available. Continuing...')

    print(colored(heading('Deploying Listing'), 'yellow'))
    listing_address = deploy_listing(w3)
    print(colored(listing_address, 'green'))
