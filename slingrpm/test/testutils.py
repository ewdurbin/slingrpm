import multiprocessing
import SimpleHTTPServer
import SocketServer

class TempServer:

  def __init__(self):
    self.handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    self.httpd = SocketServer.TCPServer(("127.0.0.1", 65001), self.handler)

  def start(self):
    self.d = multiprocessing.Process(name='serve', target=self.httpd.serve_forever)
    self.d.daemon = True
    self.d.start()

  def stop(self):
    self.d.terminate()
    self.d.join()
 
