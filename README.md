# torganizer

A stupid simple media manager with the purpose of automating a standardized media library layout out of unstructured media files.
Written in Python and probably only works in version 2.7

## Getting started

Start by cloning this repository. Then in the cloned directory:
```
python setup.py install
```

torganizer needs a yaml config file to function
```
---
loglevel: debug
logoutput: stdout
handlers:
    music:
        scan_path: /path/to/scan
        dst_path: /path/to/library
        tmp_path: /path/to/staging
        handler: MusicHandler
        lastfm_apikey: your_lastfm_apikey (optional)
```

All keys under handlers['handler'] will be added as attributes in the handler class instance.

## Music classification

The following order is used when lookup up metadata
1. (Optional) LastFM, search for artist and title based on info from 2 and 3
2. ID3 tags (or whatever tagging your choice of audio codec uses)
3. Parse file name

Using this data it constructs a naming convention as such: Artist Name/Album Name/<discId><trackNumber> - <title>.<ext>

ID3 tags are updated to reflect the information collected.

## Running it

Use the torganizer_cmd.py argsparser script to run from commandline, for usage:
```
$ python torganizer_cmd.py --help
usage: torganizer_cmd.py [-h] [--config CONFIG_PATH] [--src SRC]

Torrent Organizer script

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG_PATH  Path to torganizer config yaml
  --src SRC             Source folder to organize
```

## Extending it

Currently only mp3 music file support is added. But flac, ogg, whatever can easily be added
by subclassing torganizer.files.SoundFile and adding some ways to retrieve and store metadata.
Adding support for video files is on the todo
