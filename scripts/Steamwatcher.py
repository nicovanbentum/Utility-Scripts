""" This Python modules describes an application that checks for active steam downloads
and shuts down the computer when they are all finished. """

import os
import time
import subprocess
import winreg as reg
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
        file = open(steam_path + "/steamapps/LibraryFolders.vdf", 'r')
    except OSError:
        print("Unable to open {}.".format(steam_path + "/steamapps/LibraryFolders.vdf"))

    # parse Valve's weird cfg format (its like a shitty version of JSON)
    # we strip all whitespace and new lines, strip the line of any starting
    # and ending " characters, then split on "" to seperate the two elements
    # there's probably a cleaner way to do this but whatever.
    tostrip = ['\t', '\n']
    for line in file:
        for c in tostrip:
            line = line.replace(c, '')
        line = line.strip('"')
        line = line.split("\"\"")
        if line[0].isdigit():
            fp = line[1] + "\\steamapps\\downloading"
            if os.path.isdir(fp):
                dirs.append(fp)
    return dirs

DIRS = get_download_dirs()

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
        print('\033[1m' + "Updating..")
        last_size = get_all()
        time.sleep(60)
        new_size = get_all()

    print("Finishing up..")
    time.sleep(300)
    print("     Updating" + '\033[92m' + " finished.")
    print("Shutting down..")
    subprocess.call(["shutdown", "/s"])

main()

    