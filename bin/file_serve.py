#!/usr/bin/env python2

import sys
import os
import os.path

from slingrpm import filetrans
import sys

server = filetrans.SlingerFileServer(sys.argv[1])
server.serve()
