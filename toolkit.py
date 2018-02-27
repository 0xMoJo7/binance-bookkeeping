from client import BinanceRESTAPI, BinanceWebSocketAPI
import config

rest_client = BinanceRESTAPI(config.KEY, config.SECRET)
ws_client = BinanceWebSocketAPI(config.KEY)

def ping():
    return rest_client.ping()

def last_day_market_stats():
    prices = rest_client.all_prices()
    for price in prices:
        print price.symbol, price.price

def my_trade_by_pair(pair):
    trades = rest_client.my_trades("{0}".format(pair))
    for trade in trades:
        print trade.id, trade.price, trade.qty
