__author__ = 'johan'

import os
import re
import logging
from torganizer.utils import sanitize_string, occurrence_in_string, unicode_squash

logger = logging.getLogger(__name__)


def soundfile_factory(f):
    """
    Factory that returns suitable SoundFile class for file 'f'

    :param f: filename of file
    :type f: str
    :return: subclass of SoundFile
    :rtype: SoundFile
    """
    formats = {
        '.mp3': SoundFileMP3
    }
    try:
        ext = os.path.splitext(f)[1]
        return formats[ext]
    except KeyError:
        logger.warning("No factory for file type %s, falling back on generic" % f)
        return SoundFileGeneric


class SoundFile(object):
    """
    Base SoundFile class, use SoundFileGeneric class if you don't
    want to utilize any metadata analytics
    """
    def __init__(self, filename):
        self.filename_path = filename
        self.filename = os.path.basename(filename)
        self.filename_wext, self.extension = os.path.splitext(self.filename)
        self.artist_name = None
        self.album_name = None
        self.track_number = None
        self.title_name = None
        self.parse_filename()

    def parse_filename(self):
        """
        TODO: refine logic

        :return:
        """
        try:
            self.track_number = re.search(r"^([0-9]+)", self.filename_wext).group()
        except AttributeError, ex:
            logger.error("Could not parse file name %s, hope it contains any metadata. Exception was" % self.filename,
                         str(ex))
        else:
            occurrence = occurrence_in_string('-', self.filename_wext)

            # assume "trackno - title"
            if occurrence == 1:
                self.title_name = sanitize_string(self.filename_wext.split('-')[1], title=False)

            # assume "trackno - artist - title"
            elif occurrence == 2:
                self.artist_name = sanitize_string(self.filename_wext.split('-')[1], title=True)
                self.title_name = sanitize_string(self.filename_wext.split('-')[2], title=False)

            # assume "trackno - artist - album - title"
            elif occurrence == 3:
                self.artist_name = sanitize_string(self.filename_wext.split('-')[1], title=True)
                self.album_name = sanitize_string(self.filename_wext.split('-')[2], title=True)
                self.title_name = sanitize_string(self.filename_wext.split('-')[3], title=False)

            # no match
            else:
                occurrence = occurrence_in_string('.', self.filename_wext)

                # could be "trackno title" or just "title"
                # but we could easily trash titles starting with digits
                if occurrence == 0:
                    self.title_name = sanitize_string(re.sub("^[0-9]+", "", self.filename_wext.split('.')[0]),
                                                      title=False)

                # assume "trackno. title"
                elif occurrence == 1:
                    self.title_name = sanitize_string(self.filename_wext.split('.')[1], title=False)

    @staticmethod
    def sanitize_tracknumber(n):
        return "%02d" % int(n.split("/")[0])

    def __str__(self):
        """
        Returns the calculated file name
        File metadata takes precedence over whatever information was encoded in the previous filename
        Squashes utf characters to minimize encoding problems for any tools accessing the file

        :return:
        """
        # This should be configurable
        return "%s - %s%s" % (self.sanitize_tracknumber(self.track_number), unicode_squash(self.title_name),
                              self.extension)


class SoundFileMP3(SoundFile):
    """
    The MP3 sound file analyzer
    """
    def __init__(self, filename):
        super(SoundFileMP3, self).__init__(filename=filename)

        from mutagen.easyid3 import EasyID3
        self.id3 = EasyID3(self.filename_path)
        try:
            self.artist_name = self.id3['artist']
        except KeyError:
            logger.warning("No artist name metadata found for %s" % self.filename)
        try:
            self.album_name = self.id3['album']
        except KeyError:
            logger.warning("No album name metadata found for %s" % self.filename)
        try:
            self.title_name = self.id3['title']
        except KeyError:
            logger.warning("No title metadata found for %s" % self.filename)
        try:
            self.track_number = self.id3['tracknumber']
        except KeyError:
            logger.warning("No track number metadata found for %s" % self.filename)


class SoundFileGeneric(SoundFile):
    """
    Dummy class inherited from SoundFile, use for just parsing filename for details
    """
    pass