import os
import json
import urllib
import locale
import time
import random
import yaml
import logging
from logging.handlers import RotatingFileHandler
from prometheus_client import start_http_server, Gauge

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler = RotatingFileHandler('exporter.log', maxBytes = 100 * 1024 * 1024, backupCount = 5)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# get the keys
with open('keys.yml', 'r') as stream:
    try:
        keys = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        logging.exception("Failed to read keys ...")
        quit()

os.environ['WEB3_INFURA_API_KEY'] = keys["infura-api"]

from web3.auto.infura import w3

if w3.isConnected() == True:
    logger.info("Connected to the ethereum network")
else:
    logger.error("Can't connect to the eth network")
    quit()

locale.setlocale(locale.LC_ALL, '')

# get top contracts
with open('topContracts.yml', 'r') as stream:
    try:
        topDaiHolderContracts = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        logger.exception('Failed to read topContracts')
        quit()

# https://changelog.makerdao.com/releases/mainnet/1.1.2/contracts.json
daiAddress = w3.toChecksumAddress('0x6b175474e89094c44da98b954eedeac495271d0f')
potAddress = w3.toChecksumAddress('0x197E90f9FAD81970bA7976f33CbD77088E5D7cf7')

def loadContract(address):
    abisite = f'http://api.etherscan.io/api?module=contract&action=getabi&address={address}&apikey={keys["etherscan-api"]}&format=raw'
    with urllib.request.urlopen(abisite) as url:
        abi = json.loads(url.read())
    return w3.eth.contract(address = w3.toChecksumAddress(address), abi = abi)


def contractDaiBalance(address):
    DAIBalance = daiContract.functions.balanceOf(w3.toChecksumAddress(address)).call()
    balanceEth = w3.fromWei(DAIBalance, 'ether')
    logger.debug(f'Address {address} holds {balanceEth:n} DAI')
    return balanceEth


def contractDaiTotalSupply():
    erc20_dai_supply = daiContract.functions.totalSupply().call()
    balanceEth = w3.fromWei(erc20_dai_supply, 'ether')
    logger.debug(f'Total DAI supply is {balanceEth:n}')
    return balanceEth


def dsrBalance():
    dsr_balance = potContract.functions.Pie().call()
    chi = potContract.functions.chi().call()
    multiply = dsr_balance*chi/10**27
    balance_eth = w3.fromWei(multiply, 'ether')
    logger.debug(f'DSR locked value is {balance_eth:n} DAI')
    return balance_eth


balanceGauge = Gauge(
    'top_contracts_dai_balance',
    'Top contracts DAI balance',
    labelnames = ['contract'])

erc20_dsr_Gauge = Gauge(
    'dai_ERC20_dsr',
    'ERC20 (floating supply) vs dai in DSR',
    labelnames = ['supply'])

start_http_server(8000)

# load the contracts
daiContract = loadContract(daiAddress)
potContract = loadContract(potAddress)

while True:
    for contractAddress in topDaiHolderContracts:
        balanceGauge.labels(contract = topDaiHolderContracts[contractAddress]['desc']).set(contractDaiBalance(contractAddress))

    erc20_dsr_Gauge.labels(supply='ERC20').set(contractDaiTotalSupply())
    erc20_dsr_Gauge.labels(supply='DSR').set(dsrBalance())
    time.sleep(10)
