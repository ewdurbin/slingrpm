import time
import zmq

from multiprocessing import Process
from multiprocessing import Queue 
from multiprocessing import Pipe 


class serverProcess(Process):

  all_open_parent_conns = []

  def __init__(self):
    super(serverProcess, self).__init__() 
    self.daemon = True
    self.port = None 

    self.child_conn, self.parent_conn = Pipe(duplex = False)
    serverProcess.all_open_parent_conns.append(self.parent_conn)
    self.port_queue = Queue(1)

    self.start()
    self.child_conn.close()

  def run(self):
    for conn in serverProcess.all_open_parent_conns:
      conn.close()

    self.context0 = zmq.Context(1)
    self.socket0 = self.context0.socket(zmq.REP)
    self.socket0.bind('tcp://*:64500')

    self.port = "foo"
    self.port_queue.put(self.port)
    self.port_queue.close()
    self.child_conn.close()

    print "bound to 64500" 
    print "server: begin recv obj"
    print self.socket0.recv_pyobj()
    print "server: end recv obj"
  
    print "server: begin send obj"
    msg = {'from': 0}
    self.socket0.send_pyobj(msg)
    print "server: end send obj"
  
    self.socket0.close()

  def get_port(self):
    self.parent_conn.close()
    return self.port_queue.get()

def client():
  context1 = zmq.Context()

  socket1 = context1.socket(zmq.REQ)
  socket1.connect('tcp://%s:%s' % ('localhost', 64500))
  print "connected to tcp://127.0.0.1:64500" 
  
  print "client: begin send obj"
  msg = {'from': 1}
  socket1.send_pyobj(msg)
  print "client: end send obj"

  print "client: begin recv obj"
  print socket1.recv_pyobj() 
  print "client: end recv obj"

  socket1.close()

def server():
  context0 = zmq.Context(1)

  socket0 = context0.socket(zmq.REP)
  socket0.bind('tcp://*:64500')
  print "bound to 64500" 

  print "server: begin recv obj"
  print socket0.recv_pyobj()
  print "server: end recv obj"

  print "server: begin send obj"
  msg = {'from': 0}
  socket0.send_pyobj(msg)
  print "server: end send obj"

  socket0.close()

def async():
  c = Process(target=client)
  print c.is_alive()

  s = serverProcess()
  print s.is_alive()
  print "PORT " + s.get_port()

  c.daemon = True
  print c.daemon

  c.start()
  print c.is_alive()

  c.join()
  s.join()

if __name__ == '__main__':
  async()

