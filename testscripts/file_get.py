from filetrans import CatcherFilePuller
import sys

puller = CatcherFilePuller(sys.argv[0], sys.argv[1], '*', sys.argv[2])
puller.get_file()
