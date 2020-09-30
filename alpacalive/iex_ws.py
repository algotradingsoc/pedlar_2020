# pyEX 
# https://pypi.org/project/socketIO-client-nexus/ 0.7.6 or above

from socketIO_client_nexus import SocketIO, BaseNamespace
import json
import zmq


_SIO_URL_PREFIX = 'https://ws-api.iextrading.com'
_SIO_PORT = 443


def _tryJson(data, raw=True):
    '''internal'''
    if raw:
        return data
    try:
        return json.loads(data)
    except ValueError:
        return data


class WSClient(object):
    def __init__(self, addr, tickers=None, on_data=None, on_open=None, on_close=None, raw=False, tcp='tcp://127.0.0.1:7000'):
        '''
           addr: path to sio
           sendinit: tuple to emit
           on_data, on_open, on_close: functions to call
       '''

        # Socket to talk to server
        # Global variable as need to pass to function 
        context = zmq.Context()
        zmqsocket = context.socket(zmq.PUB)
        zmqsocket.connect(tcp)
        print('IEX publisher connect to port 7000')
        
        # connect to correct socket 
        self.addr = addr
        self.tickers = tickers

        on_data = on_data or print

        class Namespace(BaseNamespace):
            def on_connect(self, *data):
                if on_open:
                    on_open(_tryJson(data, raw))

            def on_disconnect(self, *data):
                if on_close:
                    on_close(_tryJson(data, raw))

            def on_message(self, data):
                prased = _tryJson(data, raw)
                on_data(prased)
                zmqsocket.send_multipart([bytes('IEX', 'utf-8'), bytes(json.dumps(prased), 'utf-8')])

        self._Namespace = Namespace

    def run(self):
        self.socketIO = SocketIO(_SIO_URL_PREFIX, _SIO_PORT)
        self.namespace = self.socketIO.define(self._Namespace, self.addr)
        for t in self.tickers:
            if self.addr == '/1.0/tops':
                self.namespace.emit('subscribe', t)
                print('Subscribe to IEX {}'.format(t))
            if self.addr == '/1.0/deep':
                subscribe_dict = {'channels':['deep']}
                subscribe_dict['symbols'] = [t]
                self.namespace.emit('subscribe', json.dumps(subscribe_dict))
                print('Subscribe to IEX DEEP {}'.format(t))
        self.socketIO.wait()


if __name__=="__main__":

    import sys

    try: 
        mode = sys.argv[1]
    except IndexError:
        mode = 'TOPS'
    
    tickers = sys.argv[2:]

    if mode == 'TOPS':
        IEX_TOPS = WSClient('/1.0/tops', tickers)
        IEX_TOPS.run()
    else:
        IEX_DEEP = WSClient('/1.0/deep', tickers)
        IEX_DEEP.run()

