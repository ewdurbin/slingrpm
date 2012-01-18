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

    print 'Sending check message'
    socket.send_pyobj(msg)
    data = socket.recv_pyobj()
    if data['body'] == 'NO FILE':
      print data
      raise Exception
    if data['body'] == 'CANNOT SERVE THAT':
      print data
      raise Exception
    if data['body'] == 'FILE INCOMING':
      print 'GET: opening file for writing'
      dest = open(self.destpath, 'w+')  
    else:
      raise Exception

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
        else:
          continue
      else:
        msg['loc'] = 'DONE'
        socket.send_pyobj(msg)
        break   
