from web3 import web3, Web3
import time
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


web3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/")) #http provider either etherium or bsc rpc || Currently this script is made to arb between dexes that run on same chain (ex: dex1=bnb,dex2+bnb )
default_address = "" # your bnb public address
private_key = "" #wallet private key
Token_contract ="" #Contract address of the token you want to buy
wbnb_contract = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c" #contract address of  wbnb
wbnb_value = 0 #amount of wbnb u want to spend on the buy
buy_tax =  0 #Tokens buy tax amount (this varies from token to token)
sell_tax = 0 #Tokens Sell tax amount (this varies from token to token)
dex_router_address_1 = "" #router address of the DEX_01
dex_abi_1 = '' #abi of the DEX_01
dex_router_address_2 = "" #router address of DEX_02
dex_abi_2 = '' #abi of DEX_2


def check_connection(): # function to check connection with the rpc...
    return web3.isConnected()

def dex_buy(address_router,address_abi): #function to buy tokens from dex
    contract = web3.eth.contract(address=address_router, abi=address_abi)

    nonce = web3.eth.get_transaction_count(default_address)

    start = time.time()

    txn = contract.functions.swapExactETHForTokens(
        0,  #amoubt of tokens to recieve (min)
        [wbnb_contract, Token_contract],
        default_address,
        (int(time.time()) + 10000)
    ).buildTransaction({
        'from': default_address,
        'value': web3.toWei(wbnb_value, 'ether'),
        'gas': 2000000,
        'gasPrice': web3.toWei('50', 'gwei'),
        'nonce': nonce,
    })

    signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
    tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print("Recipt >> " + web3.toHex(tx_token))

def dex_sell(address_router,address_abi): #function to sell tokens from dex
    contract = web3.eth.contract(address=address_router, abi=address_abi)

    nonce = web3.eth.get_transaction_count(default_address)

    start = time.time()

    txn = contract.functions.swapExactTokensForTokens(
        0,  # amoubt of tokens to recieve (min)
        [wbnb_contract, Token_contract],
        default_address,
        (int(time.time()) + 10000)
    ).buildTransaction({
        'from': default_address,
        'gas': 500000,
        'gasPrice': web3.toWei('50', 'gwei'),
        'nonce': nonce,
    })

    signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
    tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print("Recipt >> " + web3.toHex(tx_token))

def Token_price(tokenContract, router, router_abi,): #Function to fetch the price of token on the dex
  Contract = web3.eth.contract(address=router,   abi=router_abi)
  Token = web3.toWei(1, 'Ether')
  price = Contract.functions.getAmountsOut(Token,   [tokenContract, wbnb_contract]).call()
  humanredable = web3.fromWei(price[1],'ether')
  x = humanredable / 100000
  print(x)

def precentage_difference(p_1,p_2):  #calculating precentage difference of token price between the two DEXs..
    if p_1 > p_2:
        a = (p_1-p_2)/(p_1+p_2/2)*100
        return a
    else:
        b = (p_2 - p_1) / (p_2 + p_1 / 2) * 100
        return b

tax_f = buy_tax + sell_tax  # total of buy/sell tax
tax_format = tax_f + 5 #0.05 or 5% | adjust this value to your liking..

i = 5

while i == 5:
    try:
        if check_connection() == True:
            if precentage_difference(Token_price(Token_contract,dex_router_address_1,dex_abi_1),Token_price(Token_contract,dex_router_address_2,dex_abi_2)) > tax_format:
                if Token_price(Token_contract,dex_router_address_1,dex_abi_1) < Token_price(Token_contract,dex_router_address_2,dex_abi_2):
                    dex_buy(dex_router_address_1,dex_abi_1)
                    time.sleep(8)
                    dex_sell(dex_router_address_2,dex_abi_2)
                    time.sleep(5)
                    quit()  # remove quit() if you wish to continue after an arb...
                else:
                    dex_buy(dex_router_address_2, dex_abi_2)
                    time.sleep(8)
                    dex_sell(dex_router_address_1, dex_abi_1)
                    time.sleep(5)
                    quit()
            else:
                print("searching for arb opportunity.....")
    except:
        print("Connection Error with HTTP-PROVIDER")