import constant
import sys
from heroprotocol.versions import latest, list_all, build
import mpyq
from datetime import datetime


class ParseHelper:
    """
    Class is used to make interfacing with the hero protocol library a bit easier.

    Methods
    -------

    initProtocols(replayPath):F
        Handles initializing the protocol library and getting the corresponding protocol.

    filetime_to_dt(s)
        Handles converting the file time structure to a regular date time.

    loopsToSeconds(s)
        Converts game loops to actual seconds.

    getDetails()
        Gets the game details.

    getInitData()
        Gets some initialization data from the game.

    getTrackerEvents()
        Gets the tracker events from the game.

    getProtocol()
        Returns the internal protocol found for the parsed replay.
    """

    def __init__(self):
        """
        Initiailizes an instance of this class.

        """
        self.archive = ''
        self.protocol = ''

    def initProtocols(self, replayPath: str) -> None:
        """
        Initializes the protocols needed to parse the passed in replay

        Parameters
        ----------
        replayPath: str
            Path to the replay.
        """
        self.archive = mpyq.MPQArchive(replayPath)
        self.protocol = self._getProtocol()

    def filetime_to_dt(self, s: int) -> datetime:
        """
        Returns a datetime object from passed in filetime.

        Parameters
        ----------
        s: int
            Filetime to convert.

        Returns
        -------
        The datetime from the passed in filetime.

        """
        return datetime.fromtimestamp((s - 116444736000000000) // 10000000)

    def loopsToSeconds(self, loops: int) -> int:
        """
        Returns the seconds from a gameloop.

        Parameters
        ----------
        loops: int
            The number of loops the game has performed.

        Returns
        -------
        The seconds from gameloops.

        Remarks
        -------
        Game loops aren't seconds. They start at 610 and the server tick is 16 fps.

        """
        return int((loops - 610) / 16)

    def _getProtocol(self):
        """
        Handles getting the internal protocol.

        Returns
        -------
        A Python module object.
        """
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
        """
        Handles getting the a list of details.

        Returns
        -------
        a list of players.
        """
        contents = self.archive.read_file(constant.ARCHIVE_DETAILS)
        return self.protocol.decode_replay_details(contents)

    def getInitData(self):
        """
        Handles getting initial data of the game.

        Returns
        ------
        Initial game data.
        """
        contents = self.archive.read_file(constant.ARCHIVE_INIT_DATA)
        return self.protocol.decode_replay_initdata(contents)

    def getTrackerEvents(self):
        """
        Handles getting tracking data of the game.

        Returns
        ------
        Tracking events from the replay.
        """
        return self.archive.read_file(constant.ARCHIVE_TRACKER_EVENTS)

    def getProtocol(self):
        """
        Returns the protocol used to parse the replay.

        Returns
        ------
        The porotocol used to parse the replay.
        """
        return self.protocol
