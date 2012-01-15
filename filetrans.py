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

    msg = {'loc': 0,
           'path': self.srcpath}

    print 'Sending check message'
    socket.send_pyobj(msg)
    data = socket.recv_pyobj()
    if data['body'] == 'NO FILE':
      print data
      raise Exception
    if data['body'] == 'CANNOT SERVE THAT':
      print data
      raise Exception

    print 'GET: opening file for writing'
    dest = open(self.destpath, 'w+')  
 
    while True:
      socket.send_pyobj(msg)
      data = socket.recv_pyobj()
      if data['body']:
        dest.write(data['body'])
        msg['loc'] = dest.tell()
      else:
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

    file = sock.recv_pyobj()
    if not os.path.isfile(file['path']):
      print file['path']
      sock.send_pyobj({'body': 'NO FILE'})
      sock.close()
      return
    if not os.path.dirname(file['path']).startswith(self.servedir):
      sock.send_pyobj({'body': 'CANNOT SERVE THAT'})
      sock.close()
      return

    sock.send_pyobj({'body': 'FILE INCOMING'})
 
    BUFF = 32768 

    while True:
      ret = {}
      msg = sock.recv_pyobj()
      if not os.path.isfile(msg['path']):
        sock.send_pyobj({'body': 'NO FILE'})
        continue
      fn = open(msg['path'], 'rb')
      fn.seek(msg['loc'])
      ret['body'] = fn.read(BUFF)
      ret['loc'] = fn.tell()
      sock.send_pyobj(ret)
