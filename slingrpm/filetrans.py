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
 
    ret = {'body': None,
           'loc': None,
           'crc': 0}
    with FileHandler(file['path'], 32768) as fh:
      while True:
        msg = sock.recv_pyobj()
        if msg['loc'] == 'DONE':
          break
        ret['body'] = fh.read(msg['loc'])
        ret['crc'] = zlib.crc32(ret['body'],ret['crc'])
        ret['loc'] = fh.tell()
        sock.send_pyobj(ret)

class FileHandler:

  def __init__(self, file, buffer=32768):
    self.file_path = file
    self.buffer = buffer
    if os.path.isfile(file):
