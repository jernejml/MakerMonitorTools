import os
import json
import urllib
import locale
import time
import random
import yaml
from prometheus_client import start_http_server, Gauge

# get the keys
with open('keys.yml', 'r') as stream:
    try:
        keys = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        quit()

os.environ['WEB3_INFURA_API_KEY'] = keys["infura-api"]

from web3.auto.infura import w3

if w3.isConnected() == True:
    print("Connected to the ethereum network")
else:
    print("Can't connect to the eth network")
    quit()

locale.setlocale(locale.LC_ALL, '')

# get top contracts
with open('topContracts.yml', 'r') as stream:
    try:
        topDaiHolderContracts = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        quit()

# https://changelog.makerdao.com/releases/mainnet/1.1.2/contracts.json
daiAddress = w3.toChecksumAddress('0x6b175474e89094c44da98b954eedeac495271d0f')
potAddress = w3.toChecksumAddress('0x197E90f9FAD81970bA7976f33CbD77088E5D7cf7')

def loadContract(address):
    abisite = f'http://api.etherscan.io/api?module=contract&action=getabi&address={address}&apikey={keys["etherscan-api"]}&format=raw'
    with urllib.request.urlopen(abisite) as url:
        abi = json.loads(url.read())
    return w3.eth.contract(address = address, abi = abi)


def contractDaiBalance(address):
    DAIBalance = daiContract.functions.balanceOf(address).call()
    balanceEth = w3.fromWei(DAIBalance, 'ether')
    return balanceEth


def contractDaiTotalSupply():
    erc20_dai_supply = daiContract.functions.totalSupply().call()
    balanceEth = w3.fromWei(erc20_dai_supply, 'ether')
    return balanceEth


def dsrBalance():
    dsr_balance = potContract.functions.Pie().call()
    chi = potContract.functions.chi().call()
    multiply = dsr_balance*chi
    balance_eth = w3.fromWei(multiply, 'ether')
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
