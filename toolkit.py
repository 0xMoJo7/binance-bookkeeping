from client import BinanceRESTAPI, BinanceWebSocketAPI
import config
import json
import pandas as pd

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

def account_balances_df():
    balances_df = pd.DataFrame(columns=['asset', 'free', 'locked'])
    account = rest_client.account()
    for balance in account.balances:
        if float(balance.free) > 0.0 or float(balance.locked) > 0.0:
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
            pass
    return trade_history_df

def portfolio_value():
    market_df = market_prices()
    balances_df = account_balances_df()
    portfolio_df = pd.merge(balances_df, market_df, on='asset', how='inner')
    portfolio_df['usd_value'] = ''
    btc_usd = market_df.loc[market_df['asset'] =='BTCUSDT']
    print btc_usd
    for kv, row in portfolio_df.iterrows():
        total_holding = row['free'] + row['locked']
        usd = total_holding * float(btc_usd['price'])
        row['usd_value'] = usd
    print portfolio_df


