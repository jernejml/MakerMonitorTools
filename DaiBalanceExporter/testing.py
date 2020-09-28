import os
import json
import urllib
import locale
import time
import random
import yaml
from prometheus_client import start_http_server, Gauge

with open('keys.yml', 'r') as stream:
    try:
        keys = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print("Can't read keys: " + exc)

os.environ['WEB3_INFURA_API_KEY'] = keys["infura-api"]

from web3.auto.infura import w3

if w3.isConnected() == True:
    print("Connected to the ethereum network")
else:
    print("Can't connect to the eth network")
    quit()

locale.setlocale(locale.LC_ALL, '')

daiAddress = w3.toChecksumAddress('0x6b175474e89094c44da98b954eedeac495271d0f')

def loadContract(address):
    abisite = f'http://api.etherscan.io/api?module=contract&action=getabi&address={address}&apikey={keys["etherscan-api"]}&format=raw'
    with urllib.request.urlopen(abisite) as url:
        abi = json.loads(url.read())
    return w3.eth.contract(address = address, abi = abi)

def yDAICurveBalance():
    # get balance
    yDAIBalance = yDAIVaultContract.functions.balances(0).call()
    balanceEth = w3.fromWei(yDAIBalance, 'ether')
    print(f'Curve Y pool yDAI balance: {balanceEth:n}')
    return balanceEth

def mooniswapDaiUsdcBalance():
    # get balance
    DAIBalance = mooniswapDaiUsdcContract.functions.getBalanceForRemoval(daiAddress).call()
    balanceEth = w3.fromWei(DAIBalance, 'ether')
    print(f'Mooniswap DAI-USDC pool DAI balance: {balanceEth:n}')
    return balanceEth

def uniswapDaiUsdcBalance():
    UniDaiUsdcContract = '0xAE461cA67B15dc8dc81CE7615e0320dA1A9aB8D5'
    DAIBalance = daiContract.functions.balanceOf(UniDaiUsdcContract).call()
    balanceEth = w3.fromWei(DAIBalance, 'ether')
    print(f'Uniswap DAI-USDC pool DAI balance: {balanceEth:n}')
    return balanceEth

def aaveDaiBalance():
    AaveDaiContract = '0x3dfd23A6c5E8BbcFc9581d2E864a68feb6a076d3'
    DAIBalance = daiContract.functions.balanceOf(AaveDaiContract).call()
    balanceEth = w3.fromWei(DAIBalance, 'ether')
    print(f'Aave DAI pool balance: {balanceEth:n}')
    return balanceEth


CURVE_Y_BALANCE_GAUGE = Gauge('curveY_balance', 'Curve Y DAI vault balance')
MOONISWAP_DAI_USDC_BALANCE_GAUGE = Gauge('mooniswap_dai_usdc_balance', 'Mooniswap DAI-USDC pool balance')
UNISWAP_DAI_USDC_BALANCE_GAUGE = Gauge('uniswap_dai_usdc_balance', 'Uniswap DAI-USDC pool balance')
AAVE_DAI_BALANCE_GAUGE = Gauge('aave_dai_balance', 'Aave DAI balance')

start_http_server(8000)

# load the contracts
yDAIVaultContract = loadContract('0x45F783CCE6B7FF23B2ab2D70e416cdb7D6055f51')
mooniswapDaiUsdcContract = loadContract('0x31631b3DD6C697E574d6B886708cd44f5ccf258F')
daiContract = loadContract(daiAddress)

while True:
    CURVE_Y_BALANCE_GAUGE.set(yDAICurveBalance())
    MOONISWAP_DAI_USDC_BALANCE_GAUGE.set(mooniswapDaiUsdcBalance())
    UNISWAP_DAI_USDC_BALANCE_GAUGE.set(uniswapDaiUsdcBalance())
    AAVE_DAI_BALANCE_GAUGE.set(aaveDaiBalance())
    time.sleep(10)
