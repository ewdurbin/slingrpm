import konira

import testutils
from multiprocessing import Process
import time
import os
import os.path
import zmq

from slingrpm import SlingerFileServer 

def testclient(port, msg):
  context = zmq.Context()

  socket = context.socket(zmq.REQ)
  socket.connect('tcp://%s:%s' % ('127.0.0.1', port))

  print "sending message"
  socket.send_pyobj(msg)

  return socket.recv_pyobj()

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

class serverProcess(Process):
  def __init__(self):
    super(serverProcess, self).__init__() 
    self.context0 = zmq.Context(1)
    self.socket0 = self.context0.socket(zmq.REP)
    self.socket0.bind('tcp://*:64500')
    print "bound to 64500" 

  def run(self):
    print "server: begin recv obj"
    print self.socket0.recv_pyobj()
    print "server: end recv obj"
  
    print "server: begin send obj"
    msg = {'from': 0}
    self.socket0.send_pyobj(msg)
    print "server: end send obj"
  
    self.socket0.close()

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


describe "receiving a package with SlingerFileServer":
 
  before all:
    testutils.setuprepos()

  before each:
    pass
 
  it "accepts a directory path to serve from":
    server = SlingerFileServer('testarea/repo')
    assert server

  it "raises an Exception for directories which do not exist":
    raises Exception: server = SlingerFileServer('testarea/norepo')

  it "has a serve method which returns a nonzero port for valid directory":
    server = SlingerFileServer('testarea/repo') 
    assert server.port != 0

  it "runs a useless test":
    c = Process(target=client)
    print c.is_alive()
  
    s = serverProcess()
    print s.is_alive()
  
    c.daemon = True
    print c.daemon
    s.daemon = True
    print s.daemon
  
    c.start()
    print c.is_alive()
  
    s.start()
    print s.is_alive()
  
    c.join()
    s.join()
    assert True == True

#  it "accepts a message asking for a file as path , and responds with FILE INCOMING if file exists":
#    server = SlingerFileServer('testarea/repo')
#    server.start()
#    msg = {'loc': 0, 'path': os.path.join(os.getcwd(), 'testarea/repo/.slingrpm.conf')}
#    data = testclient(server.port, msg) 
#    assert data['body'] == "FILE INCOMING"
#    server.stop()

  after each:
    pass
    
  after all:
    testutils.teardownrepos()
