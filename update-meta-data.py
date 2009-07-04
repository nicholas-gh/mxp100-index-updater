#!/usr/bin/python

import sys
import os

ROOT = sys.argv[1]

PLAYLIST_NAME = "Default Playlist.epl"
HDR = "".join(chr(x) for x in [0xbe,0xba,0x02,0x00,0x01,0x00] + [0x0] * 318)
BLOCK_LEN = 716

REDUNDANT_FILES=False

def has_music_children(path):
    for dir, dirs, files in os.walk(path):
        for file in files:
            if file.upper().endswith(".MP3"):
                return True
    return False

for dir, dirs, files in os.walk(ROOT):
    if PLAYLIST_NAME in files:
        os.unlink(os.path.join(dir, PLAYLIST_NAME))

for dir, dirs, files in os.walk(ROOT):
    if not REDUNDANT_FILES:
        avoid = []
        for d in dirs:
            if not has_music_children(os.path.join(dir,d)):
                avoid.append(d)
        for d in avoid:
            dirs.remove(d)
    music_files = [x for x in files if x.upper().endswith(".MP3")]
    items = []
    for entry in music_files + dirs:
        t = "a:%s/%s" % (dir[len(ROOT):], entry)
        t = t.replace("/","\\")
        # not sure why this is required
        t = t.replace("a:\\music","a:\\Music")
        items.append(t)
    playlist_fn = os.path.join(dir, PLAYLIST_NAME)
    if items or REDUNDANT_FILES:
        playlist = open(playlist_fn,"wb")
        for item in items:
            playlist.write(HDR)
            playlist.write(item)
            padding = [0x00] * (BLOCK_LEN - len(HDR) - len(item))
            playlist.write("".join(chr(x) for x in padding))
        playlist.close()
        os.chmod(playlist_fn, 0755)
        
