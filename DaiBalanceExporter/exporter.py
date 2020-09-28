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

daiAddress = w3.toChecksumAddress('0x6b175474e89094c44da98b954eedeac495271d0f')

def loadContract(address):
    abisite = f'http://api.etherscan.io/api?module=contract&action=getabi&address={address}&apikey={keys["etherscan-api"]}&format=raw'
    with urllib.request.urlopen(abisite) as url:
        abi = json.loads(url.read())
    return w3.eth.contract(address = address, abi = abi)

def contractDaiBalance(address):
    DAIBalance = daiContract.functions.balanceOf(address).call()
    balanceEth = w3.fromWei(DAIBalance, 'ether')
    return balanceEth

balanceGauge = Gauge(
    'top_contracts_dai_balance',
    'Top contracts DAI balance',
    labelnames = ['contract'])

start_http_server(8000)

# load the contracts
daiContract = loadContract(daiAddress)

while True:
    for contractAddress in topDaiHolderContracts:
        balanceGauge.labels(contract = topDaiHolderContracts[contractAddress]['desc']).set(contractDaiBalance(contractAddress))

    time.sleep(10)
