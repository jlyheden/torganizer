__author__ = 'johan'

import os
import shutil
import re
import logging
from torganizer.utils import sanitize_string, occurrence_in_string, unicode_squash, lastfm_apicall

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
        '.mp3': SoundFileMP3,
        '.flac': SoundFileMutagenGeneric,
        '.ogg': SoundFileMutagenGeneric
    }
    try:
        ext = os.path.splitext(f)[1].lower()
        return formats[ext]
    except KeyError:
        logger.warning("No factory for file type %s, falling back on generic" % f)
        return SoundFileGeneric


class SoundFile(object):
    """
    Base SoundFile class, use SoundFileGeneric class if you don't
    want to utilize any metadata analytics
    """
    def __init__(self, filename, lastfm_apikey=None):
        self.filename_path = filename
        self.filename = os.path.basename(filename)
        self.filename_wext, self.extension = os.path.splitext(self.filename)
        self.artist_name = None
        self.album_name = None
        self.track_number = None
        self.title_name = None
        self.disc_number = ''
        self.lastfm_apikey = lastfm_apikey
        self.parse_filename()

    def parse_filename(self):
        try:
            leading_digits = re.search(r"^([0-9]+)", self.filename_wext).group()
            if len(leading_digits) == 3:
                self.disc_number = leading_digits[:1]
                logger.debug("Parsed disc number '%s' from file name '%s'" % (self.disc_number, self.filename))
                self.track_number = leading_digits[1:]
            else:
                self.track_number = leading_digits
            logger.debug("Parsed track number '%s' from file name '%s'" % (self.track_number, self.filename))
        except AttributeError, ex:
            logger.error("Could not parse file name %s, hope it contains any metadata. Exception was %s" % (
                self.filename, str(ex)))
        else:
            occurrence = occurrence_in_string('-', self.filename_wext)

            # assume "trackno - title"
            if occurrence == 1:
                self.title_name = sanitize_string(self.filename_wext.split('-')[1])
                logger.debug("Parsed title name '%s' from file name '%s'" % (self.title_name, self.filename))

            # assume "trackno - artist - title"
            elif occurrence == 2:
                self.artist_name = sanitize_string(self.filename_wext.split('-')[1], title=True)
                self.title_name = sanitize_string(self.filename_wext.split('-')[2])
                logger.debug("Parsed title name '%s' from file name '%s'" % (self.title_name, self.filename))
                logger.debug("Parsed artist name '%s' from file name '%s'" % (self.artist_name, self.filename))

            # assume "trackno - artist - album - title"
            elif occurrence == 3:
                self.artist_name = sanitize_string(self.filename_wext.split('-')[1], title=True)
                self.album_name = sanitize_string(self.filename_wext.split('-')[2])
                self.title_name = sanitize_string(self.filename_wext.split('-')[3])
                logger.debug("Parsed title name '%s' from file name '%s'" % (self.title_name, self.filename))
                logger.debug("Parsed artist name '%s' from file name '%s'" % (self.artist_name, self.filename))
                logger.debug("Parsed album name '%s' from file name '%s'" % (self.album_name, self.filename))

            # no match
            else:
                occurrence = occurrence_in_string('.', self.filename_wext)

                # could be "trackno title" or just "title"
                # but we could easily trash titles starting with digits
                if occurrence == 0:
                    self.title_name = sanitize_string(re.sub("^[0-9]+", "", self.filename_wext.split('.')[0]),
                                                      title=False)
                    logger.debug("Parsed title name '%s' from file name '%s'" % (self.title_name, self.filename))

                # assume "trackno. title"
                elif occurrence == 1:
                    self.title_name = sanitize_string(self.filename_wext.split('.')[1], title=False)
                    logger.debug("Parsed title name '%s' from file name '%s'" % (self.title_name, self.filename))

    @staticmethod
    def sanitize_tracknumber(n):
        return "%02d" % int(n.split("/")[0])

    @staticmethod
    def sanitize_discnumber(n):
        return n.split("/")[0]

    def parse_lastfm_data(self):
        etree = lastfm_apicall(self.lastfm_apikey, method='track.getInfo', artist=self.artist_name,
                               track=self.title_name)
        track = etree.find('track')
        title = None
        artist = None
        track_number = None
        album = None

        try:
            title = track.find('name').text
        except AttributeError:
            logger.warning("Could not find 'name' tag from LastFM")
        else:
            logger.debug("Found title data '%s' from LastFM" % title)
            self.title_name = title

        try:
            artist = track.find('artist').find('name').text
        except AttributeError:
            logger.warning("Could not find 'artist'/'name' tag from LastFM")

        try:
            track_number = track.find('album').attrib['position']
        except AttributeError:
            logger.warning("Could not find 'position' attribute from LastFM")
        else:
            logger.debug("Found track data '%s' from LastFM" % track_number)
            self.track_number = track_number

        try:
            album = track.find('album').find('title').text
        except AttributeError:
            logger.warning("Could not find 'album'/'title' tag from LastFM")
        else:
            logger.debug("Found album data '%s' from LastFM" % album)
            self.album_name = album

    def __str__(self):
        """
        Returns the calculated file name
        File metadata takes precedence over whatever information was encoded in the previous filename
        Squashes utf characters to minimize encoding problems for any tools accessing the file

        :return:
        """
        # This should be configurable
        return sanitize_string("%s%s - %s%s" % (self.disc_number, self.sanitize_tracknumber(self.track_number),
                                                unicode_squash(self.title_name), self.extension))

    def persist(self):
        """
        Implementation specific, override in sub classes
        """
        pass

    def copy(self, dst):
        dst_full = unicode_squash(os.path.join(dst, self.artist_name, self.album_name))
        if not os.path.exists(dst_full):
            logger.debug("Destination directory '%s' does not exist. Creating it" % dst_full)
            os.makedirs(dst_full)
        shutil.copy(self.filename_path, dst_full)
        logger.info("Copied file '%s' to destination '%s'" % (self.filename_path, dst_full))


class SoundFileMP3(SoundFile):
    """
    The MP3 sound file analyzer
    """
    def __init__(self, filename):
        super(SoundFileMP3, self).__init__(filename=filename)

        from mutagen.easyid3 import EasyID3
        self.id3 = EasyID3(self.filename_path)
        try:
            self.artist_name = self.id3['artist'][0]
            logger.debug("Found artist name '%s' from ID3 tag in file '%s'" % (self.artist_name, self.filename))
        except KeyError:
            logger.warning("No artist name metadata found for %s" % self.filename)
        try:
            self.album_name = self.id3['album'][0]
            logger.debug("Found album name '%s' from ID3 tag in file '%s'" % (self.album_name, self.filename))
        except KeyError:
            logger.warning("No album name metadata found for %s" % self.filename)
        try:
            self.title_name = self.id3['title'][0]
            logger.debug("Found title name '%s' from ID3 tag in file '%s'" % (self.title_name, self.filename))
        except KeyError:
            logger.warning("No title metadata found for %s" % self.filename)
        try:
            self.track_number = self.id3['tracknumber'][0]
            self.track_number = self.sanitize_tracknumber(self.track_number)
            logger.debug("Found track number '%s' from ID3 tag in file '%s'" % (self.track_number, self.filename))
        except KeyError:
            logger.warning("No track number metadata found for %s" % self.filename)
        try:
            self.disc_number = self.id3['discnumber'][0]
            self.disc_number = self.sanitize_discnumber(self.disc_number)
            logger.debug("Found disc number '%s' from ID3 tag in file '%s'" % (self.disc_number, self.filename))
        except KeyError:
            logger.warning("No disc number metadata found for %s" % self.filename)

    def persist(self):
        self.id3['artist'] = self.artist_name
        self.id3['album'] = self.album_name
        self.id3['title'] = self.title_name
        self.id3['tracknumber'] = self.track_number
        if self.disc_number:
            self.id3['discnumber'] = self.disc_number
        self.id3.save()
        logger.debug("Committed ID3 changes: %s" % str(self.id3))
        new_path = os.path.join(os.path.dirname(self.filename_path), str(self))
        os.rename(self.filename_path, new_path)
        logger.debug("Renamed file '%s' to '%s'" % (self.filename_path, new_path))
        self.filename_path = new_path


class SoundFileMutagenGeneric(SoundFile):

    def __init__(self, filename):
        super(SoundFileMutagenGeneric, self).__init__(filename=filename)

        from mutagen import File
        self.mutagen = File(self.filename_path)
        try:
            self.artist_name = self.mutagen['artist'][0]
            logger.debug("Found artist name '%s' from metadata in file '%s'" % (self.artist_name, self.filename))
        except KeyError:
            logger.warning("No artist name metadata found for %s" % self.filename)
        try:
            self.album_name = self.mutagen['album'][0]
            logger.debug("Found album name '%s' from metadata in file '%s'" % (self.album_name, self.filename))
        except KeyError:
            logger.warning("No album name metadata found for %s" % self.filename)
        try:
            self.title_name = self.mutagen['title'][0]
            logger.debug("Found title name '%s' from metadata in file '%s'" % (self.title_name, self.filename))
        except KeyError:
            logger.warning("No title metadata found for %s" % self.filename)
        try:
            self.track_number = self.mutagen['tracknumber'][0]
            self.track_number = self.sanitize_tracknumber(self.track_number)
            logger.debug("Found track number '%s' from metadata in file '%s'" % (self.track_number, self.filename))
        except KeyError:
            logger.warning("No track number metadata found for %s" % self.filename)
        try:
            self.disc_number = self.mutagen['discnumber'][0]
            self.disc_number = self.sanitize_discnumber(self.disc_number)
            logger.debug("Found disc number '%s' from metadata in file '%s'" % (self.disc_number, self.filename))
        except KeyError:
            logger.warning("No disc number metadata found for %s" % self.filename)

    def persist(self):
        self.mutagen['artist'] = self.artist_name
        self.mutagen['album'] = self.album_name
        self.mutagen['title'] = self.title_name
        self.mutagen['tracknumber'] = self.track_number
        if self.disc_number:
            self.mutagen['discnumber'] = self.disc_number
        self.mutagen.save()
        logger.debug("Committed metadata changes: %s" % str(self.mutagen))
        new_path = os.path.join(os.path.dirname(self.filename_path), str(self))
        os.rename(self.filename_path, new_path)
        logger.debug("Renamed file '%s' to '%s'" % (self.filename_path, new_path))
        self.filename_path = new_path


class SoundFileGeneric(SoundFile):
    """
    Dummy class inherited from SoundFile, use for just parsing filename and lastfm for details
    """
    pass


class SeriesFile(object):

    def __init__(self, f):
        self.full_file_path = f
        self.filename = os.path.basename(f)
        self.file_path = os.path.dirname(f)
        self.file_ext = os.path.splitext(f)[1]
        self.series_name = None
        self.season = None
        self.episode_number = None
        self.episode_name = None
        self.parse_filename()

    def parse_filename(self):
        re_search = re.search(r"^(.*)(s[0-9]{2})(e[0-9]{2})", self.filename, re.IGNORECASE)
        self.series_name = sanitize_string(re_search.group(1), title=True, strip_dots=True)
        self.season = int(re_search.group(2).lower().lstrip('s'))
        self.episode_number = int(re_search.group(3).lower().lstrip('e'))

    def season_string(self):
        return "S%02d" % self.season

    def episode_string(self):
        return "E%02d" % self.episode_number

    def persist(self):
        new_path = os.path.join(os.path.dirname(self.full_file_path), str(self))
        os.rename(self.full_file_path, new_path)
        logger.debug("Renamed file '%s' to '%s'" % (self.full_file_path, new_path))
        self.full_file_path = new_path
        self.filename = str(self)

    def copy(self, dst):
        dst_full = unicode_squash(os.path.join(dst, self.series_name, "Season %s" % self.season))
        if not os.path.exists(dst_full):
            logger.debug("Destination directory '%s' does not exist. Creating it" % dst_full)
            os.makedirs(dst_full)
        shutil.copy(self.full_file_path, dst_full)
        logger.info("Copied file '%s' to destination '%s'" % (self.full_file_path, dst_full))

    def __str__(self):
        return sanitize_string("%s %s%s%s" % (self.series_name, self.season_string(), self.episode_string(),
                               self.file_ext))