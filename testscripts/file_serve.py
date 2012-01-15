from filetrans import SlingerFileServer
import sys

server = SlingerFileServer(sys.argv[1])
server.serve()
