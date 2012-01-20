import konira

import testutils
from multiprocessing import Process
import time
import os
import os.path
import zmq

import testutils
from slingrpm import SlingerFileServer 
from slingrpm import SlingerFileServerProcess 
from slingrpm import FileHandler 

describe "the FileHandler class":
  before all:
    testutils.setuprepos()

  before each:
    pass

  it "initializes with a filename":
    fh = FileHandler(os.path.join(os.getcwd(), 'testarea/repo/.slingrpm.conf'))
    assert fh

  it "initializes with a filename and buffersize":
    fh = FileHandler(os.path.join(os.getcwd(), 'testarea/repo/.slingrpm.conf'), 1024)
    assert fh.buffer == 1024

  it "can be called in a context block":
    with FileHandler(os.path.join(os.getcwd(), 'testarea/repo/.slingrpm.conf')) as fh:
      assert fh

  it "has a method for reading out bytes":
    fh = FileHandler(os.path.join(os.getcwd(), 'testarea/repo/.slingrpm.conf'), 8)
    assert fh.read(0)

  it "reads the right bytes":
    fh = FileHandler(os.path.join(os.getcwd(), 'testarea/repo/.slingrpm.conf'), 8)
    fhdata = fh.read(8)
    with open(os.path.join(os.getcwd(), 'testarea/repo/.slingrpm.conf'), 'rb') as fd:
      fd.seek(8)
      fddata = fd.read(8)
      assert fddata == fhdata

  it "has a method for returning current location in the file being handled":
    fh = FileHandler(os.path.join(os.getcwd(), 'testarea/repo/.slingrpm.conf'), 8)
    assert fh.tell() == 0

  it "remembers its place in a file":
    fh = FileHandler(os.path.join(os.getcwd(), 'testarea/repo/.slingrpm.conf'), 2)
    fh.read(0)
    assert fh.tell() == 2

  after each:
    pass

  after all:
    testutils.teardownrepos()

describe "receiving a package with SlingerFileServer":
 
  before all:
    testutils.setuprepos()

  before each:
    pass
 
  it "accepts a directory path to serve from":
    server = SlingerFileServer('testarea/repo')
    assert server
    server.stop()

  it "raises an Exception for directories which do not exist":
    raises Exception: server = SlingerFileServer('testarea/norepo')

  it "has a serve method which returns a nonzero port for valid directory":
    server = SlingerFileServer('testarea/repo') 
    assert server.port != 0 
    msg = {'loc': 0, 'path': os.path.join(os.getcwd(), 'testarea/repo/.slingrpm.conf')}
    data = testutils.send_msg_get_rsp(server.port, msg) 
    assert data['body'] == "FILE INCOMING"
    msg = {'loc': 'DONE', 'path': os.path.join(os.getcwd(), 'testarea/repo/.slingrpm.conf')}
    testutils.send_msg(server.port, msg) 
    server.stop()

  it "accepts a message asking for a file as path , and responds with FILE INCOMING if file exists":
    server = SlingerFileServer('testarea/repo')
    msg = {'loc': 0, 'path': os.path.join(os.getcwd(), 'testarea/repo/.slingrpm.conf')}
    data = testutils.send_msg_get_rsp(server.port, msg) 
    assert data['body'] == "FILE INCOMING"
    msg = {'loc': 'DONE', 'path': os.path.join(os.getcwd(), 'testarea/repo/.slingrpm.conf')}
    testutils.send_msg(server.port, msg) 
    server.stop()

  it "accepts a message asking for a file as path , and responds with NO FILE if file does not exist":
    server = SlingerFileServer('testarea/repo')
    msg = {'loc': 0, 'path': os.path.join(os.getcwd(), 'testarea/norepo/.slingrpm.conf')}
    data = testutils.send_msg_get_rsp(server.port, msg) 
    assert data['body'] == "NO FILE"
    server.stop()

  it "accepts a message asking for a file as path , and responds with CANNOT SERVE THAT if file is outside of servedir":
    server = SlingerFileServer('testarea/repo')
    msg = {'loc': 0, 'path': os.path.join('/etc/hosts')}
    data = testutils.send_msg_get_rsp(server.port, msg) 
    assert data['body'] == "CANNOT SERVE THAT"
    server.stop()

  after each:
    pass
    
  after all:
    testutils.teardownrepos()
