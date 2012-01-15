import zmq 
from zmq.core.error import ZMQError, ZMQBindError
import os.path

"""
Variant on thatch45's zmg file_get and file_serve
"""

class CatcherFilePuller:
  def __init__(self, destpath, srcpath, host, port):
    if os.path.isfile(destpath):
      raise Exception
    self.srcpath = srcpath
    self.host = host
    self.port = port
    self.destpath = destpath

  def get_file(self):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    buildserver = 'tcp://%s:%s' % (self.host, self.port)
    socket.connect(buildserver)
    socket.send(self.srcpath)
    
    data = socket.recv()
    if data == 'NO FILE':
      print data
      raise Exception
    if data == 'CANNOT SERVE THAT':
      print data
      raise Exception

    print 'GET: opening file for writing'
    dest = open(self.destpath, 'w+')  
    dest.write(data)
    filetowrite = True
    while filetowrite:
      data = socket.recv()
      dest.write(data)
      if not socket.getsockopt(zmq.RCVMORE):
        print 'GET: done with file'
        filetowrite = False
        socket.close()
        break

class SlingerFileServer:
  def __init__(self, servedir='/'):
    self.servedir = os.path.abspath(servedir)

  def serve(self):
    context = zmq.Context(1)
    sock = context.socket(zmq.REP)
    
    try:
      port = sock.bind_to_random_port('tcp://*', 64000, 65000, 100)
      print port
    except:
      print "ERROR"

    file = sock.recv()
    error = 0
    if not os.path.isfile(file):
      sock.send('NO FILE')
      error = 1
    if not os.path.dirname(file).startswith(self.servedir):
      sock.send('CANNOT SERVE THAT')
      error = 1
    if error:
      havemorefile = False
      sock.close()
      return
 
    fn = open(os.path.abspath(file), 'rb')
    print 'SRV: opening file'

    stream = True 
    while stream:
      stream = fn.read(128)
      if stream:
        sock.send(stream, zmq.SNDMORE)
      else:
        sock.send(stream)
        fn.close()
        print 'SRV: closing file'
