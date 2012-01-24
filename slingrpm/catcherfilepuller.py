import zmq 
from multiprocessing import Process
from multiprocessing import Queue 
import os.path
import zlib
import time

class CatcherFilePullerProcess(Process):

  def __init__(self, destpath, srcpath, host, port, status_queue=Queue(1)):
    if os.path.isfile(destpath):
      raise Exception
    super(CatcherFilePullerProcess, self).__init__()
    self.destpath = destpath
    self.srcpath = srcpath
    self.host = host
    self.port = port
    self.status_queue = status_queue
    self.msg = {'loc': 0,
                'path': self.srcpath}

  def setup_connection(self):
    self.context = zmq.Context()
    self.socket = self.context.socket(zmq.REQ)
    server = 'tcp://%s:%s' % (self.host, self.port)
    self.socket.connect(server)

  def check_file(self):
    self.socket.send_pyobj(self.msg)
    data = self.socket.recv_pyobj()
    if data['body'] != 'FILE INCOMING':
      return data['body']
    try:
      self.dest = open(self.destpath, 'w+')  
    except:
      return 'CANNOT WRITE FILE'
    return data['body']

  def get_file(self):
    crc = 0 
    while True:
      self.socket.send_pyobj(self.msg)
      data = self.socket.recv_pyobj()
      if data['body']:
        crcnew = zlib.crc32(data['body'], crc)
        if crcnew == data['crc']:
          crc = crcnew
          self.dest.write(data['body'])
          self.msg['loc'] = self.dest.tell()
        else:
          continue
      else:
        self.dest.close()
        self.msg['loc'] = 'DONE'
        self.socket.send_pyobj(self.msg)
        self.status_queue.put('FILE RECEIVED')
        break   

  def run(self):
    self.setup_connection()
    if self.check_file() == 'FILE INCOMING':
      self.get_file()
      while self.status_queue.empty():
        time.sleep(.001)
      return
    else:
      self.status_queue.put('FAILED')
      return

class CatcherFilePuller:
  def __init__(self, destpath, srcpath, host, port):
    if os.path.isfile(destpath):
      raise Exception
    self.destpath = destpath
    self.srcpath = srcpath
    self.host = host
    self.port = port
    self.status_queue = Queue(1)
    self.proc = CatcherFilePullerProcess(destpath, srcpath, host, port, self.status_queue)

  def start(self):
    self.proc.start()

  def stop(self):
    if self.proc.is_alive():
      self.proc.terminate()
      self.proc.join()
