#https://pypi.org/project/websocket_client/
import websocket
import json
import zmq
import os 


class Alpaca_Websocket():

    def __init__(self, tcp='tcp://127.0.0.1:7000',):
        
  
        # Socket to talk to server
        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.connect(tcp)
        print('Alpaca publisher connect to port 7000')
        # Set up connection to Finnhub 
        websocket.enableTrace(True)
        self.base_str = "wss://paper-api.alpaca.markets/stream"
        self.API_key = os.environ.get('APCA_API_KEY_ID')
        self.API_secret_key = os.environ.get('APCA_API_SECRET_KEY')
        if self.API_key is None:
            print('Need API key from Alpaca')

    def create_socket_funtcions(self):

        def on_message(ws, message):
            data = json.loads(message) 
            if data['stream'] == 'account_updates' or data['stream'] == 'trade_updates':
                self.socket.send_multipart([bytes('Alpaca', 'utf-8'), bytes(json.dumps(data), 'utf-8')])
            else:
                print(data)

        def on_error(ws, error):
            print(error)

        def on_close(ws):
            print("### closed ###")

        def on_open(ws):
            # Authentication 
            Authentication_payload = {
            "action": "authenticate",
            "data": {
                "key_id": self.API_key,
                "secret_key": self.API_secret_key,
                }
            }
            ws.send(json.dumps(Authentication_payload))
            print('Authenticate to Alpaca')

            # subscribe to channels 
            channels_payload = {
            "action": "listen",
            "data": {
                "streams": ["account_updates", "trade_updates"]
                }
            }
            ws.send(json.dumps(channels_payload))
            print('Subscribe to Alpaca account and trade updates')

        return on_message,on_open,on_close,on_error


    def create_socket(self):

        on_message, on_open, on_close, on_error = self.create_socket_funtcions()

        self.ws = websocket.WebSocketApp(self.base_str,
                                on_message = on_message, on_error = on_error,
                                on_close = on_close)
        self.ws.on_open = on_open
        self.ws.run_forever()
        
class Alpaca_Data_Websocket():

    def __init__(self, tcp='tcp://127.0.0.1:7000', tickers=["Q.SPY","Q.QQQ"]):
        
        # Socket to talk to server
        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.connect(tcp)
        print('Alpaca publisher connect to port 7000')
        # Set up connection to Finnhub 
        websocket.enableTrace(True)
        self.base_str = "wss://data.alpaca.markets/stream"
        self.API_key = os.environ.get('APCA_API_KEY_ID')
        self.API_secret_key = os.environ.get('APCA_API_SECRET_KEY')
        if self.API_key is None:
            print('Need API key from Alpaca')
        self.tickers = tickers 

    def create_socket_funtcions(self):

        def on_message(ws, message):
            data = json.loads(message) 
            if data['stream'] != 'listening' and data['stream'] != 'authorization' :
                self.socket.send_multipart([bytes('Alpaca', 'utf-8'), bytes(json.dumps(data), 'utf-8')])
            else:
                print(data)

        def on_error(ws, error):
            print(error)

        def on_close(ws):
            print("### closed ###")

        def on_open(ws):
            # Authentication 
            Authentication_payload = {
            "action": "authenticate",
            "data": {
                "key_id": self.API_key,
                "secret_key": self.API_secret_key,
                }
            }
            ws.send(json.dumps(Authentication_payload))
            print('Authenticate to Alpaca')

            # subscribe to channels 
            channels_payload = {
            "action": "listen",
            "data": {
                # "streams": ["T.PXY", "Q.GILD", "AM.QQQ"]
                "streams": self.tickers
                }
            }
            ws.send(json.dumps(channels_payload))
            print('Subscribe to Alpaca data')

        return on_message,on_open,on_close,on_error


    def create_socket(self):

        on_message, on_open, on_close, on_error = self.create_socket_funtcions()

        self.ws = websocket.WebSocketApp(self.base_str,
                                on_message = on_message, on_error = on_error,
                                on_close = on_close)
        self.ws.on_open = on_open
        self.ws.run_forever()

if __name__ == "__main__":

    import sys 
    endpoint = sys.argv[1]
    try:
        tickers = sys.argv[2]
    except IndexError:
        tickers = ['Q.SPY','Q.QQQ']

    if endpoint == 'data':
        Alpa_zmq = Alpaca_Data_Websocket(tickers=tickers)
        Alpa_zmq.create_socket()
    else:
        Alpa_zmq = Alpaca_Websocket()
        Alpa_zmq.create_socket()