#!~/compas_env/bin/python3.6

import sys
import os
import json
import web3
from web3 import Web3
from termcolor import colored
from computable.helpers.transaction import send
from computable.contracts import Reserve

PROVIDER_URI = 'http://mainnet.computablelabs.com:8545'
GAS_PRICE = 10
PUBLIC_KEY = os.environ.get('public_key')
PRIVATE_KEY = os.environ.get('private_key')
ETHER_TOKEN_ADDRESS = '0xb05E8B08baA9c652A0F1982889695c20aD2714a0'
MARKET_TOKEN_ADDRESS = '0x4BbD0678d0ff2e289506152F4B53090E2f9Dc4D0'
PARAMETERIZER_ADDRESS = '0x0EA44154C2FaE1621FbB31CEc4119Cc523B3702a'

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

def deploy_reserve(w3):
    abi = None
    bc = None
    with open('reserve/reserve.abi') as f:
        abi = json.loads(f.read())
    with open('reserve/reserve.bin') as f:
        bc = f.read()
    if abi is None:
        print(colored('Error reading Reserve ABI', 'red'))
        sys.exit(1)
    if bc is None:
        print(colored('Error reading Reserve Bytecode', 'red'))
        sys.exit(1)
    deployed = w3.eth.contract(abi=abi, bytecode=bc.rstrip('\n'))
    args = get_deployment_args(w3, deployed.constructor(ETHER_TOKEN_ADDRESS, MARKET_TOKEN_ADDRESS, PARAMETERIZER_ADDRESS))
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

    print(colored(heading('Ether Token Address check'), 'yellow'))
    if not ETHER_TOKEN_ADDRESS:
        sys.exit(1)
    print('Ether Token Address available. Continuing...')

    print(colored(heading('Market Token Address check'), 'yellow'))
    if not MARKET_TOKEN_ADDRESS:
        sys.exit(1)
    print('Market Token Address available. Continuing...')

    print(colored(heading('Parameterizer Address check'), 'yellow'))
    if not PARAMETERIZER_ADDRESS:
        sys.exit(1)
    print('Parameterizer Address available. Continuing...')

    print(colored(heading('Gas Price check'), 'yellow'))
    if not GAS_PRICE:
        sys.exit(1)
    print('Gas Price available. Continuing...')

    print(colored(heading('Deploying Reserve'), 'yellow'))
    reserve_address = deploy_reserve(w3)
    print(colored(reserve_address, 'green'))
