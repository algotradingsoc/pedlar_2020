

from subprocess import Popen, run, TimeoutExpired

if __name__=='__main__':
    # Start the data sources 
    p0 = Popen(['python3','alpaca_ws.py', 'acc', '["Q.TLT","Q.QQQ"]'], shell=False, stdin=None, stdout=None, stderr=None, close_fds=True)
    #p1 = Popen(['python3','alpaca_ws.py', 'data', '["Q.SPY","Q.GLD"]'], shell=False, stdin=None, stdout=None, stderr=None, close_fds=True)
    p2 = Popen(['python3','iex_ws.py','TOPS','TLT','QQQ'], shell=False, stdin=None, stdout=None, stderr=None, close_fds=True)
    print('Alpaca Stream PID {}'.format(p0.pid))
    #print('Alpaca Stream PID {}'.format(p1.pid))
    print('IEX Stream PID {}'.format(p2.pid))
    # Start Live Trading
    p3 = run(['python3','zmq_agent.py'],check=True)
    p0.kill()
    #p1.kill()
    p2.kill()

 






