""" This Python modules describes an application that checks for active steam downloads
and shuts down the computer when they are all finished. """

import os
import time
import subprocess
import winreg as reg
import pyparsing as pp
import colorama

def get_download_dirs():
    dirs = list()
    hkey = reg.OpenKey(reg.HKEY_CURRENT_USER, "Software\\Valve\\Steam")
    steam_path = reg.QueryValueEx(hkey, "SteamPath")[0]
    dl_folder = steam_path + "/steamapps/downloading"
    if os.path.isdir(dl_folder):
        dirs.append(dl_folder)

    # Read the steam vdf file that contains path strings to all
    # game install directories.
    file = None
    try:
        file = open(steam_path + "/steamapps/LibraryFolders.vdf").read()
    except OSError:
        print("Unable to open {}.".format(steam_path + "/steamapps/LibraryFolders.vdf"))

    # parse Valve's weird cfg format (its like a shitty version of JSON)
    # forward declare the value of a key
    value = pp.Forward()
    # expression for our dict structure that looks like: ["key1", value]
    key_value = pp.Group(pp.QuotedString('"') + value)
    # create a parse structure for value so value looks like: c
    expression = pp.Suppress('{') + pp.Dict(pp.ZeroOrMore(key_value)) + pp.Suppress('}')
    # set our value to be a quoted string follow by the structure we defined, looks like this in Python:
    # ["outer_key", { ["inner_key1", value], ["inner_key2", value] } ]
    # we can acess the above as either a dict or array.
    value <<= pp.QuotedString('"') | expression
    parser = pp.Dict(key_value)
    content = parser.parseString(file)
    # get the last pair's key, this should be the last folder numbered folder,
    # so we can use it as our max nr of folders for looping.
    max_folders = int(content["LibraryFolders"][-1][0])

    # loop from 1 to (incl) max folders and use it as a dictionary key to get
    # the value of that key which should be a steam library folder path.
    for i in range(1, max_folders + 1):
        libpath = content["LibraryFolders"][str(i)]
        dlpath = libpath + "\\steamapps\\downloading"
        if os.path.isdir(dlpath):
            dirs.append(dlpath)
    return dirs

DIRS = get_download_dirs()
for directory in DIRS:
    print("Found " + directory)

def get_size(start_path='.'):
    total_size = 0
    for dirpath, _, filenames in os.walk(start_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if not os.path.islink(filepath):
                total_size += os.path.getsize(filepath)
    return total_size

def get_all():
    all_sizes = list()
    for dirpath in DIRS:
        all_sizes.append(get_size(dirpath))
    return all_sizes

def updating(last_sizes, new_sizes):
    for last_size, new_size in zip(last_sizes, new_sizes):
        if new_size != last_size:
            return True
    return False

def main():
    colorama.init()
    print("Checking for active downloads.. (10 seconds timeout)")
    last_size = get_all() # random initial value
    time.sleep(10)
    new_size = get_all() # random initial value

    if last_size == new_size:
        print('\033[91m' + "No active downloads found.")
        return

    while updating(last_size, new_size):
        print('\033[1m' + "Updating.. (60 seconds timeout)")
        last_size = get_all()
        time.sleep(60)
        new_size = get_all()

    print("Finishing up..")
    time.sleep(300)
    print("     Updating" + '\033[92m' + " finished.")
    print("Shutting down..")
    subprocess.call(["shutdown", "/s"])

main()

    