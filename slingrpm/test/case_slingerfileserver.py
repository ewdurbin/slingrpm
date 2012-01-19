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

  socket.send_pyobj(msg)

  return socket.recv_pyobj()

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

  it "accepts a message asking for a file as path , and responds with FILE INCOMING if file exists":
    server = SlingerFileServer('testarea/repo')
    msg = {'loc': 0, 'path': os.path.join(os.getcwd(), 'testarea/repo/.slingrpm.conf')}
    data = testclient(server.port, msg) 
    assert data['body'] == "FILE INCOMING"
    msg = {'loc': 'DONE', 'path': os.path.join(os.getcwd(), 'testarea/repo/.slingrpm.conf')}
    data = testclient(server.port, msg) 
    server.stop()

  it "accepts a message asking for a file as path , and responds with NO FILE if file does not exist":
    server = SlingerFileServer('testarea/repo')
    msg = {'loc': 0, 'path': os.path.join(os.getcwd(), 'testarea/norepo/.slingrpm.conf')}
    data = testclient(server.port, msg) 
    assert data['body'] == "NO FILE"
    server.stop()

  it "accepts a message asking for a file as path , and responds with CANNOT SERVE THAT if file is outside of servedir":
    server = SlingerFileServer('testarea/repo')
    msg = {'loc': 0, 'path': os.path.join(os.getcwd(), '/etc/hosts')}
    data = testclient(server.port, msg) 
    assert data['body'] == "CANNOT SERVE THAT"
    server.stop()

  after each:
    pass
    
  after all:
    testutils.teardownrepos()
