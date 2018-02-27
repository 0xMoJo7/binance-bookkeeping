from client import BinanceRESTAPI, BinanceWebSocketAPI
import config

rest_client = BinanceRESTAPI(config.KEY, config.SECRET)
ws_client = BinanceWebSocketAPI(config.KEY)
