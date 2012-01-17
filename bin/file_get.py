#!/usr/bin/env python2

import sys
import os
import os.path

from slingrpm import filetrans
import sys

puller = filetrans.CatcherFilePuller(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
puller.get_file()
