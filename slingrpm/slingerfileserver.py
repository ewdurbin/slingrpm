import zmq
from multiprocessing import Process
from multiprocessing import Pipe
from multiprocessing import Queue 
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

class SlingerFileServerProcess(Process): # pragma: no cover

  all_open_parent_conns = []

  def __init__(self, servedir, buffer=32768):
    super(SlingerFileServerProcess, self).__init__()
    self.servedir = servedir
    self.buffer = buffer

    self.daemon = True
    self.port = 0

    self.child_conn, self.parent_conn = Pipe(duplex = False)
    SlingerFileServerProcess.all_open_parent_conns.append(self.parent_conn)
    self.port_queue = Queue(1)

    self.start()
    self.child_conn.close()

  def setup_connection(self):
    self.context = zmq.Context(1)  
    self.socket = self.context.socket(zmq.REP)
    try:
      port = self.socket.bind_to_random_port('tcp://*', 64000, 65000, 100)
    except:
      raise
    return port

  def check_path(self):
    file = self.socket.recv_pyobj()
    if not os.path.isfile(file['path']):
      self.socket.send_pyobj({'body': 'NO FILE'})
      self.socket.close()
      return False
    if not os.path.dirname(file['path']).startswith(self.servedir):
      self.socket.send_pyobj({'body': 'CANNOT SERVE THAT'})
      self.socket.close()
      return False
    self.servefile = file['path']
    self.socket.send_pyobj({'body': 'FILE INCOMING'})
    return True

  def serve_loop(self, fh):
    ret = {'body': None,
           'loc': None,
           'crc': 0}

    while True:
      msg = self.socket.recv_pyobj()
      if msg['loc'] == 'DONE':
        ret['body'] = 'OKAYBYE'
        self.socket.send_pyobj(ret)
        break
      ret['body'] = fh.read(msg['loc'])
      ret['crc'] = zlib.crc32(ret['body'],ret['crc'])
      ret['loc'] = fh.tell()
  
      self.socket.send_pyobj(ret)

    self.socket.close(linger=10)

  def run(self):
    for conn in SlingerFileServerProcess.all_open_parent_conns:
      conn.close()

    self.port = self.setup_connection()
    self.port_queue.put(self.port)
    self.port_queue.close()
    self.child_conn.close()

    if not self.check_path(): 
      return
  
    with FileHandler(self.servefile, self.buffer) as fh:
      self.serve_loop(fh)

  def get_port(self):
    self.parent_conn.close()
    return self.port_queue.get()

class SlingerFileServer:

  def __init__(self, servedir='/', buffer=32768):
    if os.path.isdir(os.path.abspath(servedir)):
      self.servedir = os.path.abspath(servedir)
    else:
      raise Exception 
    self.proc = SlingerFileServerProcess(self.servedir) 
    self.port = self.proc.get_port()

  def stop(self):
    self.proc.join(timeout=.1)

