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
tmp_path: /tmp/somedir
handlers:
    music:
        src: /my/src/music
        dst: /my/dst/music
        handler: MusicHandler
```

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
by subclassing torganizer.files.SoundFile and adding some ways to retrieve metadata.
Adding support for video files is on the todo
