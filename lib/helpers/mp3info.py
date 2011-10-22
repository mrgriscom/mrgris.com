import os
import os.path
import sys
import json
from mutagen.mp3 import MP3
import re

def mp3_metadata(path):
    def _id3(info, key):
        try:
            return info[key].text[0]
        except KeyError:
            return None

    info = MP3(path)
    title = _id3(info, 'TIT2')
    artist = _id3(info, 'TPE1') # game name [(system)]
    artist2 = _id3(info, 'TPE3') # system
    length = info.info.length
   
    match = re.match('^(?P<game>.+) \((?P<system>.+)\)$', artist)
    if match:
        game, system = match.group('game'), match.group('system')
    else:
        game, system = artist, None
    if artist2:
        system = artist2

    return {
        'filename': os.path.split(path)[1],
        'title': title,
        'game': game,
        'system': system,
        'length': length,
        'rating': 0,
    }

if __name__ == "__main__":

    path = sys.argv[1]
    files = [os.path.join(path, f) for f in os.listdir(path)]
    metadata = [mp3_metadata(path) for path in files]
    print json.dumps(metadata)
