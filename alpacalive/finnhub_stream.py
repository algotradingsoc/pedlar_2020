
# python3 finnhub_stream.py QQQ OANDA:GBP_USD OANDA:DE10YB_EUR 

#https://pypi.org/project/websocket_client/
import websocket
import json
import zmq


class Finnhub_Websocket():

    def __init__(self, tcp='tcp://127.0.0.1:7000', API_key=None, tickers=None):
        
        self.tickers = tickers
        # Socket to talk to server
        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.connect(tcp)
        print('Finnhub publisher connect to port 7000')
        # Set up connection to Finnhub 
        # websocket.enableTrace(True)
        self.base_str = "wss://ws.finnhub.io?token={}"
        self.API_key = API_key
        if API_key is None:
            print('Need API key from Finnhub')

    def create_socket_funtcions(self):

        def on_message(ws, message):
            data = json.loads(message) 
            if data['type'] == 'trade':
                self.socket.send_multipart([bytes('Finnhub', 'utf-8'), bytes(json.dumps(data), 'utf-8')])
                print(data['data'])
                # print(data['data'][0]['p'])

        def on_error(ws, error):
            print(error)

        def on_close(ws):
            print("### closed ###")

        def on_open(ws):
            topic_dict = {"type":"subscribe"}
            for ticker in self.tickers:
                topic_dict["symbol"] = ticker
                ws.send(json.dumps(topic_dict))
                print('Subscribe to Finnhub {}'.format(ticker))
            # Send at least one ticker? 
            # ws.send('{"type":"subscribe","symbol":"BINANCE:BTCUSDT"}') # 24 hours trading 
        return on_message,on_open,on_close,on_error


    def create_socket(self):

        on_message, on_open, on_close, on_error = self.create_socket_funtcions()

        self.ws = websocket.WebSocketApp(self.base_str.format(self.API_key),
                                on_message = on_message, on_error = on_error,
                                on_close = on_close)
        self.ws.on_open = on_open
        self.ws.run_forever()
        


if __name__ == "__main__":

    import sys 
    try:
        tickers = sys.argv[1:]
    except IndexError:
        tickers = ['AAPL','BINANCE:BTCUSDT']

    Finn_zmq = Finnhub_Websocket(tickers=tickers)
    Finn_zmq.create_socket()


