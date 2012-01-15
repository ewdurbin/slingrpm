from filetrans import CatcherFilePuller
import sys

puller = CatcherFilePuller(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
puller.get_file()
