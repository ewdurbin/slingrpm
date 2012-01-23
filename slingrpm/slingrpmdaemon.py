import ConfigParser
import zmq
import os.path
from multiprocessing import Process
from multiprocessing import Queue

class SlingRPMDaemonProcess(Process):

  def __init__(self, config):
    super(SlingRPMDaemonProcess, self).__init__()
    self.config = config
    self.listenport = self.config.get('SlingRPMDaemon', 'listenport')

  def runloop(self):
    while True:
      msg = self.socket.recv_pyobj()
      ret = {}
      if msg['body'] == "ALIVE?":
        ret['body'] = "YES"

      self.socket.send_pyobj(ret)

  def run(self):
    self.context = zmq.Context(10)
    self.socket = self.context.socket(zmq.REP)
    try:
      self.socket.bind('tcp://*:%s' % self.listenport)
    except:
      raise
    self.runloop()

class SlingRPMDaemon:

  def __init__(self, conf='/etc/slingrpm/daemon.conf'):
    self.read(conf)

  def read(self, conf):
    if not os.path.isfile(conf):
      raise Exception
    self.conf = conf

    try:
      config = ConfigParser.RawConfigParser()
      config.read(self.conf)
      self.config = config

      self.listenport = self.config.get('SlingRPMDaemon', 'listenport')
    except:
      raise

  def start(self):
    self.proc = SlingRPMDaemonProcess(self.config)
    self.proc.start()

  def stop(self):
    if self.proc.is_alive():
      self.proc.terminate()
      self.proc.join(.01)

if __name__ == "__main__":
  import slingrpm
  daemon = SlingRPMDaemon()
  slingrpm.daemonize()
  daemon.start()
