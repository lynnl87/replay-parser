import constant
import sys
from heroprotocol.versions import latest, list_all, build
import mpyq
import datetime

# This class is basically an easy to use wrapper around the heroprotocol library.
# I previously would of initialized the archive in the constructor, but if we are
# parsing multiple replays, we want build() to keep track of the protocols rather
# than losing them each class instantiation.
class ParseHelper:
    def __init__(self):
        self.archive = ''
        self.protocol = ''

    def initProtocols(self, replayPath):
        self.archive = mpyq.MPQArchive(replayPath)
        self.protocol = self._getProtocol()

    def filetime_to_dt(self, s):
        return datetime.datetime.fromtimestamp((s - 116444736000000000) // 10000000)

    # game loops aren't seconds. They start at 610 and go 16 frames a second.
    def loopsToSeconds(self, loops):
        return (loops - 610) / 16

    # handles getting the protocol we need for this specific replay.
    def _getProtocol(self):
        contents = self.archive.header['user_data_header']['content']
        header = latest().decode_replay_header(contents)
        baseBuild = header['m_version']['m_baseBuild']
        try:
            newProto = build(baseBuild)
        except:
            print('Unsupported base build: %d' % baseBuild)
            sys.exit(1)
        return newProto

    def getDetails(self):
        contents = self.archive.read_file(constant.ARCHIVE_DETAILS)
        return self.protocol.decode_replay_details(contents)

    def getInitData(self):
        contents = self.archive.read_file(constant.ARCHIVE_INIT_DATA)
        return self.protocol.decode_replay_initdata(contents)
        
    def getTrackerEvents(self):
        return self.archive.read_file(constant.ARCHIVE_TRACKER_EVENTS)

    def getProtocol(self):
        return self.protocol
