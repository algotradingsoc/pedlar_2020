import sys
import json
import logging
import os
import pandas as pd 
import zmq
import datetime


# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)

# Connect to tcp ports for pricing/news and different sources 
# Each message send will have a topic indicating the pricing source and then the actual content 
socket.bind('tcp://127.0.0.1:7000')
socket.setsockopt_string(zmq.SUBSCRIBE, 'IEX')
socket.setsockopt_string(zmq.SUBSCRIBE, 'Finnhub')
socket.setsockopt_string(zmq.SUBSCRIBE, 'Alpaca')


## Trade logic can be implemented here where 
## For live trading, we recommend using Alpaca paper trade account 
def ondata(pricingsource, tickdata):

    if (pricingsource == 'IEX') or (pricingsource == 'Finnhub') or (pricingsource == 'Alpaca') :
        try:
            d = json.loads(tickdata)
            print(d)
        except json.decoder.JSONDecodeError:
            print('Not decoded')









if __name__=='__main__':

    counter = 0
    while True:
        message = socket.recv_multipart()
        exchange = message[0].decode()
        tick = message[1]
        ondata(exchange,tick)
        counter += 1
