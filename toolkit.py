from client import BinanceRESTAPI, BinanceWebSocketAPI
import config
import json
import pandas as pd

rest_client = BinanceRESTAPI(config.KEY, config.SECRET)
ws_client = BinanceWebSocketAPI(config.KEY)

def ping():
    return rest_client.ping()

def last_day_market_stats():
    prices = rest_client.all_prices()
    for price in prices:
        return price.symbol, price.price

def my_trade_by_pair(pair):
    trades = rest_client.my_trades("{0}".format(pair))
    for trade in trades:
        return trade.id, trade.price, trade.qty

def account_balances():
    account = rest_client.account()
    for balance in account.balances:
        print balance.asset, balance.free, balance.locked # build dateframe here to return
