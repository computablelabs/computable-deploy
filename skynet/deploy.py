#!/home/rob/py_36/bin/python3.6

import sys
import os
import json
import web3
from web3 import Web3
from web3.middleware import geth_poa_middleware
from termcolor import colored
from computable.helpers.account import lock, unlock
from computable.helpers.transaction import call, send
from computable.contracts import EtherToken
from computable.contracts import MarketToken
from computable.contracts import Voting
from computable.contracts import Parameterizer
from computable.contracts import Reserve
from computable.contracts import Datatrust
from computable.contracts import Listing

PROVIDER_URI = 'http://skynet.computablelabs.com:8545'
GAS_PRICE = 3
PUBLIC_KEY = os.environ.get('public_key')
PRIVATE_KEY = os.environ.get('private_key')

def heading(val):
    return f'************* {val} *************'

def get_w3():
    provider = web3.HTTPProvider(PROVIDER_URI)
    w3 = Web3(provider)
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
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

    # computable.py sets the nonce
    # curr_nonce = w3.eth.getTransactionCount(w3.eth.defaultAccount)

    # build the args for the send method
    args = get_deployment_args(w3, deployed.constructor())
    # use computable.py's ability to sign offline
    tx_hash = send(w3, PRIVATE_KEY, args)
    # wait for it... TODO adjust timeout
    tx_rct = w3.eth.waitForTransactionReceipt(tx_hash)
    return tx_rct['contractAddress']

def deploy_market_token(w3):
    abi = None
    bc = None
    with open('markettoken/markettoken.abi') as f:
        abi = json.loads(f.read())
    with open('markettoken/markettoken.bin') as f:
        bc = f.read()
    if abi is None:
        print(colored('Error reading Market Token ABI', 'red'))
        sys.exit(1)
    if bc is None:
        print(colored('Error reading Ether Token Bytecode', 'red'))
        sys.exit(1)
    deployed = w3.eth.contract(abi=abi, bytecode=bc.rstrip('\n'))
    args = get_deployment_args(w3, deployed.constructor(PUBLIC_KEY, 0))
    tx_hash = send(w3, PRIVATE_KEY, args)
    tx_rct = w3.eth.waitForTransactionReceipt(tx_hash)
    return tx_rct['contractAddress']

def deploy_voting(w3, market_token_address):
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
    args = get_deployment_args(w3, deployed.constructor(market_token_address))
    tx_hash = send(w3, PRIVATE_KEY, args)
    tx_rct = w3.eth.waitForTransactionReceipt(tx_hash)
    return tx_rct['contractAddress']

def get_parameterizer_opts():
    return {
        'price_floor': Web3.toWei(500, 'kwei'), # 5e5
        'spread': 110,
        'list_reward': Web3.toWei(2, 'ether'), # 2e18
        'stake': Web3.toWei(10, 'ether'), # 1e19
        'vote_by': 900, # 15 mins
        'plurality': 50,
        'backend_payment': 5,
        'maker_payment': 70,
        'cost_per_byte': Web3.toWei(550, 'mwei') # 5.5e8 -> about 11/mbyte cents atm
        }

def deploy_parameterizer(w3, market_token_address, voting_address):
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
            market_token_address,
            voting_address,
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

def deploy_reserve(w3, ether_token_address, market_token_address, parameterizer_address):
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
    args = get_deployment_args(w3, deployed.constructor(ether_token_address, market_token_address, parameterizer_address))
    tx_hash = send(w3, PRIVATE_KEY, args)
    tx_rct = w3.eth.waitForTransactionReceipt(tx_hash)
    return tx_rct['contractAddress']

def deploy_datatrust(w3, ether_token_address, voting_address, parameterizer_address, reserve_address):
    abi = None
    bc = None
    with open('datatrust/datatrust.abi') as f:
        abi = json.loads(f.read())
    with open('datatrust/datatrust.bin') as f:
        bc = f.read()
    if abi is None:
        print(colored('Error reading Datatrust ABI', 'red'))
        sys.exit(1)
    if bc is None:
        print(colored('Error reading Datatrust Bytecode', 'red'))
        sys.exit(1)
    deployed = w3.eth.contract(abi=abi, bytecode=bc.rstrip('\n'))
    args = get_deployment_args(w3, deployed.constructor(ether_token_address, voting_address, parameterizer_address, reserve_address))
    tx_hash = send(w3, PRIVATE_KEY, args)
    tx_rct = w3.eth.waitForTransactionReceipt(tx_hash)
    return tx_rct['contractAddress']

def deploy_listing(w3, market_token_address, voting_address, parameterizer_address, reserve_address, datatrust_address):
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
    args = get_deployment_args(w3, deployed.constructor(market_token_address, voting_address, parameterizer_address, reserve_address, datatrust_address))
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

    print(colored(heading('Deploying Ether Token'), 'yellow'))
    ether_token_address = deploy_ether_token(w3)
    print(colored(ether_token_address, 'green'))

    print(colored(heading('Deploying Market Token'), 'yellow'))
    market_token_address = deploy_market_token(w3)
    print(colored(market_token_address, 'green'))

    print(colored(heading('Deploying Voting'), 'yellow'))
    voting_address = deploy_voting(w3, market_token_address)
    print(colored(voting_address, 'green'))

    print(colored(heading('Deploying Parameterizer'), 'yellow'))
    parameterizer_address = deploy_parameterizer(w3, market_token_address, voting_address)
    print(colored(parameterizer_address, 'green'))

    print(colored(heading('Deploying Reserve'), 'yellow'))
    reserve_address = deploy_reserve(w3, ether_token_address, market_token_address, parameterizer_address)
    print(colored(reserve_address, 'green'))

    print(colored(heading('Deploying Datatrust'), 'yellow'))
    datatrust_address = deploy_datatrust(w3, ether_token_address, voting_address, parameterizer_address, reserve_address)
    print(colored(datatrust_address, 'green'))

    print(colored(heading('Deploying Listing'), 'yellow'))
    listing_address = deploy_listing(w3, market_token_address, voting_address, parameterizer_address, reserve_address, datatrust_address)
    print(colored(listing_address, 'green'))


    print(colored(heading('Set Market Token privileged'), 'yellow'))
    print(colored('instantiating MarketToken', 'blue'))
    market_token = MarketToken(PUBLIC_KEY)
    market_token.at(w3, market_token_address)
    print(colored('Setting addresses...', 'blue'))
    mt_gas = market_token.deployed.functions.setPrivileged(reserve_address, listing_address).estimateGas()
    mt_args = market_token.set_privileged(reserve_address, listing_address, {'gas': mt_gas, 'gas_price': w3.toWei(GAS_PRICE, 'gwei')})
    mt_tx_hash = send(w3, PRIVATE_KEY, mt_args)
    mt_tx_rct = w3.eth.waitForTransactionReceipt(mt_tx_hash)
    print(colored(mt_tx_rct, 'green'))

    print(colored(heading('Set Voting privileged'), 'yellow'))
    print(colored('instantiating Voting', 'blue'))
    voting = Voting(PUBLIC_KEY)
    voting.at(w3, voting_address)
    print(colored('Setting addresses...', 'blue'))
    v_gas = voting.deployed.functions.setPrivileged(parameterizer_address, datatrust_address, listing_address).estimateGas()
    v_args = voting.set_privileged(parameterizer_address, datatrust_address, listing_address, {'gas': v_gas, 'gas_price': w3.toWei(GAS_PRICE, 'gwei')})
    v_tx_hash = send(w3, PRIVATE_KEY, v_args)
    v_tx_rct = w3.eth.waitForTransactionReceipt(v_tx_hash)
    print(colored(v_tx_rct, 'green'))

    print(colored(heading('Set Datatrust privileged'), 'yellow'))
    print(colored('instantiating Datatrust', 'blue'))
    datatrust = Datatrust(PUBLIC_KEY)
    datatrust.at(w3, datatrust_address)
    print(colored('Setting addresses...', 'blue'))
    d_gas = datatrust.deployed.functions.setPrivileged(listing_address).estimateGas()
    d_args = datatrust.set_privileged(listing_address, {'gas': d_gas, 'gas_price': w3.toWei(GAS_PRICE, 'gwei')})
    d_tx_hash = send(w3, PRIVATE_KEY, d_args)
    d_tx_rct = w3.eth.waitForTransactionReceipt(d_tx_hash)
    print(colored(d_tx_rct, 'green'))
