""" This Python modules describes an application that checks for active steam downloads
and shuts down the computer when they are all finished. """

import os
import time
import signal
import threading
import subprocess
import winreg as reg
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import pyparsing as pp
import colorama

class Watcher:
    def __init__(self):
        self.directories = set()
        self.loaded_steam = False

    def ask(self):
        folder = tk.filedialog.askdirectory()
        self.directories.add(folder)
    
    def load_steam_folders(self):
        if self.loaded_steam:
            return

        hkey = reg.OpenKey(reg.HKEY_CURRENT_USER, "Software\\Valve\\Steam")
        steam_path = reg.QueryValueEx(hkey, "SteamPath")[0]
        dl_folder = steam_path + "/steamapps/downloading"
        if os.path.isdir(dl_folder):
            self.directories.add(dl_folder)
        # Read the steam vdf file that contains path strings to all
        # game install directories.
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
                self.directories.add(dlpath)
        self.loaded_steam = True

    def folder_size(self, start_path='.'):
        total_size = 0
        for dirpath, _, filenames in os.walk(start_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if not os.path.islink(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size

    def folder_sizes(self):
        all_sizes = list()
        for dirpath in self.directories:
            all_sizes.append(self.folder_size(dirpath))
        return all_sizes

    def is_updating(self, last_sizes: list, new_sizes: list):
        for last_size, new_size in zip(last_sizes, new_sizes):
            if new_size != last_size:
                return True
        return False

    def clear(self):
        self.directories.clear()
        self.loaded_steam = False

    def get_folders(self):
        return self.directories

class Application:
    def __init__(self):
        self.watcher = Watcher()
        
        self.window = tk.Tk()
        self.window.title("Download Watcher")
        self.window.geometry('500x360')
        
        button_frame = tk.Frame(self.window)
        button_frame.pack(side=tk.BOTTOM)

        self.logger = tk.Text(self.window, height=100, width=100)
        self.logger.pack(side=tk.LEFT)
        self.logger.tag_config("green", foreground="green")
        self.logger.tag_config("red", foreground="red")

        self.steam_btn = tk.Button(button_frame, text="Add Steam",
        command=self.load_steam_folders)
        self.steam_btn.pack(side=tk.LEFT)
        
        self.folder_btn = tk.Button(button_frame, text="Add Folder",
        command=self.ask)
        self.folder_btn.pack(side=tk.LEFT)

        self.clear_btn = tk.Button(button_frame, text="Clear", 
        command=self.clear)
        self.clear_btn.pack(side=tk.LEFT)
        
        self.start_btn = tk.Button(button_frame, text="Start",
        command=self.watch_thread)
        self.start_btn.pack(side=tk.LEFT)

        self.stop_btn = tk.Button(button_frame, text="Stop",
        command=self.stop)
        self.stop_btn.pack(side=tk.LEFT)

        self.thread = None
        self.running = False

        self.timer = threading.Event()
        self.window.protocol("WM_DELETE_WINDOW", self.on_exit)
        signal.signal(signal.SIGINT, self.stop)

    def log(self, text: str, color="black"):
        self.logger.config(state=tk.NORMAL)
        self.logger.insert(tk.END, text, (color))
        self.logger.config(state=tk.DISABLED)

    def ask(self):
        if self.running:
            tkinter.messagebox.showwarning("Warning", "Please stop the Watcher.")
            return
        folders_copy = self.watcher.get_folders().copy()
        self.watcher.ask()
        for folder in self.watcher.get_folders():
            if folder not in folders_copy:
                self.log("Added: ", color="green")
                self.log(folder + '\n')

    def clear(self):
        if self.running:
            tkinter.messagebox.showwarning("Warning", "Please stop the Watcher.")
            return
        self.watcher.clear()
        self.logger.config(state=tk.NORMAL)
        self.logger.delete('1.0', tk.END)
        self.logger.config(state=tk.DISABLED)

    def load_steam_folders(self):
        if self.running:
            tkinter.messagebox.showwarning("Warning", "Please stop the Watcher.")
            return
        folders_copy = self.watcher.get_folders().copy()
        self.watcher.load_steam_folders()
        for folder in self.watcher.get_folders():
            if folder not in folders_copy:
                self.log("Added: ", color="green")
                self.log(folder + '\n')

    def watch(self):
        self.running = True
        self.timer.clear()
        self.log("Checking for active downloads.. \n")
        
        last_size = self.watcher.folder_sizes() # random initial value
        self.timer.wait(timeout=10)
        new_size = self.watcher.folder_sizes() # random initial value

        if self.timer.is_set():
            self.log("Watcher stopped. \n", color="red")
            self.running = False
            return

        if last_size == new_size:
            self.log("No active downloads found. \n", color="red")
            self.running = False
            return
        else:
            self.log("Updates ")
            self.log("found. \n", color="green")
            self.log("Updating.. \n")
 
        while self.watcher.is_updating(last_size, new_size):
            last_size = self.watcher.folder_sizes()
            if not self.timer.is_set():
                self.timer.wait(timeout=60)

            if self.timer.is_set():
                self.log("Watcher stopped. \n", color="red")
                self.running = False
                return
            new_size = self.watcher.folder_sizes()

        self.log("Finishing up.. \n")
        self.timer.wait(timeout=300)
        self.log("Updating finished. \n")
        self.log("Shutting down computer. \n")
        self.running = False
        #subprocess.call(["shutdown", "/s"])

    def watch_thread(self):
        if self.running:
            tkinter.messagebox.showwarning("Warning", "Please stop the Watcher.")
            return
        self.thread = threading.Thread(target=self.watch)
        self.thread.start()

    def stop(self):
        if not self.running:
            return
        self.running = False
        self.timer.set()

    def run(self):
        self.window.mainloop()

    def on_exit(self):
        if self.running:
            tkinter.messagebox.showwarning("Warning", "Please stop the Watcher.")
        else:
            self.window.destroy()

def main():
    app = Application()
    app.run()

if __name__ == "__main__":
    main()

    