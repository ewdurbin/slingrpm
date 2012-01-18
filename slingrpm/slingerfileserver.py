import zmq
import os.path
import zlib

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
      self.fd = open(self.file_path)

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.fd.close()

  def read(self, loc):
    self.fd.seek(loc)
    return self.fd.read(self.buffer)

  def tell(self):
    return self.fd.tell()

