import zmq 
import os.path
import zlib

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

    socket.send_pyobj(msg)
    data = socket.recv_pyobj()
    if data['body'] == 'NO FILE':
      raise Exception
    if data['body'] == 'CANNOT SERVE THAT':
      raise Exception
    if data['body'] == 'FILE INCOMING':
      dest = open(self.destpath, 'w+')  
    else:
      raise Exception # pragma: no cover

    crc = 0 
    while True:
      socket.send_pyobj(msg)
      data = socket.recv_pyobj()
      if data['body']:
        crcnew = zlib.crc32(data['body'], crc)
        if crcnew == data['crc']:
          crc = crcnew
          dest.write(data['body'])
          msg['loc'] = dest.tell()
        else: # pragma: no cover
          continue
      else:
        msg['loc'] = 'DONE'
        socket.send_pyobj(msg)
        break   
