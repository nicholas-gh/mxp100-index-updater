#!/usr/bin/python

import sys
import os
import pynotify

pynotify.init("e.Digital MXP100")

if len(sys.argv) != 2:
    print "Usage: %s PATH_TO_MXP_DISK" % sys.argv[0]
    sys.exit(2)
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

def pack_block(item):
        padding_bytes = [0x00] * (BLOCK_LEN - len(HDR) - len(item))
        padding = "".join(chr(x) for x in padding_bytes)
        return "".join([HDR, item, padding])

def pack_list(items):
    result_list = []
    if items == None:
        result_list.append(pack_block("a:\\Music"))
    else:
        for item in items:
            item = "a:/Music/%s" % item
            item = item.replace("/","\\")
            result_list.append(pack_block(item))
    return "".join(result_list)

def write_playlist(dirname, items=None):
    playlist_fn = os.path.join(dirname, PLAYLIST_NAME)
    playlist = open(playlist_fn,"wb")
    playlist.write(pack_list(items))
    playlist.close()
    os.chmod(playlist_fn, 0755)


music_dir = None
try:
    for dir in os.listdir(ROOT):
        if dir.upper() == "MUSIC":
            music_dir = dir
except OSError, e:
    # we'll fall through to the music_dir == None check
    pass

if music_dir == None:
    n = pynotify.Notification("e.Digital MXP100 Sync", 
                              "Unable to find music folder in %s" % ROOT,
                              "gtk.STOCK_INFO")
    n.set_urgency(pynotify.URGENCY_CRITICAL)
    n.set_timeout(pynotify.EXPIRES_NEVER)
    n.show()
    sys.exit(2)

notify_start = pynotify.Notification("e.Digital MXP100 Sync", 
                                     "Indexing started.", 
                                     "gtk.STOCK_INFO")
notify_start.set_urgency(pynotify.URGENCY_LOW)
notify_start.show()

os.system("chmod -R u+w %s" % ROOT)

for dir, dirs, files in os.walk(ROOT):
    if PLAYLIST_NAME in files:
        os.unlink(os.path.join(dir, PLAYLIST_NAME))

write_playlist(ROOT)

albums = []
for potentialalbum in os.listdir(os.path.join(ROOT,music_dir)):
    if has_music_children(os.path.join(ROOT,music_dir,potentialalbum)):
        albums.append(potentialalbum)

write_playlist(os.path.join(ROOT,music_dir), albums)

for album in albums:
    direntries = os.listdir(os.path.join(ROOT,music_dir,album))
    for direntry in direntries:
        if has_music_children(os.path.join(ROOT,music_dir,album,direntry)):
            n = pynotify.Notification("e.Digital MXP100 Sync", 
                                      "Nested folders not supported:\n<b>   %s/%s</b>\nThis music will be ignored." % (album, direntry), 
                                      "gtk.STOCK_INFO")
            n.set_urgency(pynotify.URGENCY_CRITICAL)
            n.show()
    tracks     = [x for x in direntries if x.upper().endswith(".MP3")]
    tracks.sort() # we should try read the id3 tags?
    write_playlist(os.path.join(ROOT,music_dir,album),
                   ["%s/%s" % (album, track) for track in tracks])

notify_start.close()
n = pynotify.Notification("e.Digital MXP100 Sync", "Index update completed.", "gtk.STOCK_INFO")
n.set_urgency(pynotify.URGENCY_NORMAL)
#n.set_timeout(pynotify.EXPIRES_NEVER)
n.show()

os.system("umount %s" % ROOT)
