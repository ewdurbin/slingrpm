import zmq
from multiprocessing import Process
import sys
import os.path
import zlib

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

class SlingerFileServerProcess(Process):
  def __init__(self, servedir):
    super(SlingerFileServerProcess, self).__init__()
    self.servedir = servedir
    self.context = zmq.Context(1)  
    self.socket = self.context.socket(zmq.REP)
    try:
      port = self.socket.bind_to_random_port('tcp://*', 64000, 65000, 100)
    except:
      raise
    self.port = port

  def run(self):
    print "server: begin recv obj"
    file = self.socket.recv_pyobj()
    print "server: end recv obj"
    if not os.path.isfile(file['path']):
      self.socket.send_pyobj({'body': 'NO FILE'})
      self.socket.close()
      return
    if not os.path.dirname(file['path']).startswith(self.ervedir):
      self.socket.send_pyobj({'body': 'CANNOT SERVE THAT'})
      self.socket.close()
      return
  
    self.socket.send_pyobj({'body': 'FILE INCOMING'})
  
    ret = {'body': None,
           'loc': None,
           'crc': 0}
    with FileHandler(file['path'], 32768) as fh:
      while True:
        msg = self.socket.recv_pyobj()
        if msg['loc'] == 'DONE':
         break
        ret['body'] = fh.read(msg['loc'])
        ret['crc'] = zlib.crc32(ret['body'],ret['crc'])
        ret['loc'] = fh.tell()
  
    self.socket.send_pyobj(ret)
    self.socket.close()

class SlingerFileServer:

  def __init__(self, servedir='/'):
    if os.path.isdir(os.path.abspath(servedir)):
      self.servedir = os.path.abspath(servedir)
    else:
      raise Exception 
    self.proc = SlingerFileServerProcess(self.servedir) 
    self.proc.daemon = True
    self.port = self.proc.port

  def start(self):
    self.proc.start()

  def stop(self):
    self.proc.socket.setsockopt(zmq.LINGER, -1)
    self.proc.socket.close()
    self.proc.join()

