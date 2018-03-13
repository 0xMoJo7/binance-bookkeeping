from client import BinanceRESTAPI, BinanceWebSocketAPI
import config
import json
import pandas as pd
from datetime import datetime

today = datetime.now().strftime('%Y-%m-%d %H:%M')
rest_client = BinanceRESTAPI(config.KEY, config.SECRET)
ws_client = BinanceWebSocketAPI(config.KEY)

def ping():
    return rest_client.ping()

def market_prices():
    market_df = pd.DataFrame(columns=['asset', 'price'])
    prices = rest_client.all_prices()
    for price in prices:
        market_df = market_df.append({'asset' : str(price.symbol), 'price' : price.price}, ignore_index=True)
    return market_df

def my_trades_by_pair(pair):
    trade_df = pd.DataFrame(columns=['id', 'price', 'quantity'])
    trades = rest_client.my_trades("{0}".format(pair))
    for trade in trades:
        trade_df = trade_df.append({'id': trade.id,
                                    'price' : trade.price,
                                    'quantity' : trade.qty}, ignore_index=True)
    return trade_df

def place_limit_buy(pair, quantity, price):
    buy_order = client.order_limit_buy(symbol=str(pair), quantity=str(quantity), price=str(price))
    return buy_order

def place_limit_sell(pair, quantity, price):
    sell_order = client.order_limit_sell(symbol=str(pair), quantity=str(quantity), price=str(price))
    return sell_order

def check_order_status(pair, order_id):
    order_status = client.get_order(symbol=str(pair), orderId=str(order_id))
    return order_status

def cancel_order(pair, order_id):
    result = client.cancel_order(symbol=str(pair), orderId=str(order_id))
    return result

def account_balances_df():
    balances_df = pd.DataFrame(columns=['asset', 'free', 'locked'])
    account = rest_client.account()
    for balance in account.balances:
        if balance.asset == 'BTC':
            balances_df = balances_df.append({'asset': str(balance.asset) + 'USDT',
                                              'free': float(balance.free),
                                              'locked': float(balance.locked)}, ignore_index=True)
        elif float(balance.free) > 0.0 or float(balance.locked) > 0.0:
            balances_df = balances_df.append({'asset': str(balance.asset) + 'BTC',
                                              'free': float(balance.free),
                                              'locked': float(balance.locked)}, ignore_index=True)
    return balances_df

def trade_history():
    trade_history_df = pd.DataFrame(columns=['id', 'asset', 'price', 'quantity'])
    balances_df = account_balances_df()
    for kv, row in balances_df.iterrows():
        if row['asset'] != 'BTC':
            asset_trades_df = my_trades_by_pair('{0}BTC'.format(row['asset']))
            for k, trade in asset_trades_df.iterrows():
                trade_history_df = trade_history_df.append({'id' : trade['id'],
                                                            'asset': row['asset'],
                                                            'price': trade['price'],
                                                            'quantity' : trade['quantity']}, ignore_index=True)
        else:
            asset_trades_df = my_trades_by_pair('BTCUSDT')
            for k, trade in asset_trades_df.iterrows():
                trade_history_df = trade_history_df.append({'id' : trade['id'],
                                                            'asset': row['asset'],
                                                            'price': trade['price'],
                                                            'quantity' : trade['quantity']}, ignore_index=True)
    return trade_history_df

def portfolio_value():
    market_df = market_prices()
    balances_df = account_balances_df()
    portfolio_df = pd.merge(balances_df, market_df, on='asset', how='inner')
    portfolio_df['usd_value'] = ''
    btc_usd = market_df.loc[market_df['asset'] =='BTCUSDT']
    i = 0
    for kv, row in portfolio_df.iterrows():
        if row['asset'] != 'BTCUSDT':
            total_holding = row['free'] + row['locked']
            usd = float(row['price']) * float(btc_usd['price'])
            portfolio_df['usd_value'][i] = usd * total_holding
            i += 1
        elif row['asset'] == 'BTCUSDT':
            total_holding = row['free'] + row['locked']
            usd = total_holding * float(btc_usd['price'])
            portfolio_df['usd_value'][i] = usd
            i += 1
    return portfolio_df

def portfolio_to_csv():
    today = datetime.now().strftime('%Y-%m-%d %H:%M')
    portfolio_df = portfolio_value()
    total_value = round(portfolio_df['usd_value'].sum(),2)
    stats = str(today) + ',' + str(total_value)
    with open('history.csv', 'ab') as f:
        f.write(stats + '\n')