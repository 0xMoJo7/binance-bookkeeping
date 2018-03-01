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
        print price.symbol, price.price

def my_trades_by_pair(pair):
    trades = rest_client.my_trades("{0}".format(pair))
    for trade in trades:
        return trade.id, trade.price, trade.qty

def account_balances():
    account = rest_client.account()
    for balance in account.balances:
        print balance.asset, balance.free, balance.locked

def account_balances_df():
    balances_df = pd.DataFrame(columns=['asset', 'free', 'locked'])
    account = rest_client.account()
    for balance in account.balances:
        if float(balance.free) > 0.0 or float(balance.locked) > 0.0:
            balances_df = balances_df.append({'asset': str(balance.asset), 'free': float(balance.free), 'locked': float(balance.locked)}, ignore_index=True)
    return balances_df

def trade_history():
    trade_history_df = pd.DataFrame(columns=['id', 'asset', 'price', 'quantity'])
    balances_df = account_balances_df()
    for kv, row in balances_df.iterrows():
        if row['asset'] != 'BTC':
            asset_trades_df = my_trades_by_pair('{0}BTC'.format(row['asset']))
            for kv, trade in asset_trades_df.iterrows():
                trade_history_df.append({'id' : trade['id'], 'asset': row['asset'][0], 'price': trade['price'], 'quantity' : trade['quantity']})
        else:
            pass
    return trade_history_df