import slingrpm

import zmq
import zlib
import os.path
import shutil

class Catcher:

  def __init__(self, config, host, port, file):
    self.config = config
    self.host = host
    self.port = port
    self.file = file
    self.filename = os.path.basename(file)
    self.destpath = os.path.join(self.config.packagedir, self.filename)
    self.incomingpath = os.path.join(self.config.packagedir, '.slingrpmincoming', self.filename)
    if not os.path.isdir(os.path.dirname(self.incomingpath)):
      os.makedirs(os.path.dirname(self.incomingpath))

    self.setup_socket()

    self.msg = {'loc': 0,
                'path': self.file}

  def setup_socket(self):
    self.context = zmq.Context()
    self.socket = self.context.socket(zmq.REQ)
    self.server = 'tcp://%s:%s' % (self.host, self.port)
    self.socket.connect(self.server)

  def check_file(self):
    self.socket.send_pyobj(self.msg)
    data = self.socket.recv_pyobj()
    if data['body'] != 'FILE INCOMING':
      return data['body']
    if os.path.isfile(self.destpath):
      raise Exception('FILE EXISTS')
    try:
      self.incoming = open(self.incomingpath, 'w+')  
    except:
      raise Exception('CANNOT WRITE FILE')
    return data['body']

  def get_file(self):
    if not self.check_file() == "FILE INCOMING":
      return
    crc = 0 
    while True:
      self.socket.send_pyobj(self.msg)
      data = self.socket.recv_pyobj()
      if data['body']:
        crcnew = zlib.crc32(data['body'], crc)
        if crcnew == data['crc']:
          crc = crcnew
          self.incoming.write(data['body'])
          self.msg['loc'] = self.incoming.tell()
        else:
          continue
      else:
        self.incoming.close()
        shutil.move(self.incomingpath, self.destpath) 
        self.msg['loc'] = 'DONE'
        self.socket.send_pyobj(self.msg)
        break   
