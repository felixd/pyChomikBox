#!/usr/bin/env python
from __future__ import unicode_literals

import os.path
import logging
import time
import argparse

import requests

from ChomikBox.ChomikBox import Chomik, ChomikUploader, ChomikDownloader, ChomikFolder, ChomikFile
from ChomikBox.utils.FileTransferProgressBar import FileTransferProgressBar

# This program uploads file, then downloads it in another path
# Both are done with beautiful progressbars and pauses at middle
# It was used to test if pyChomikBox works and if files are the same and not corrupt
# It can be used as code example, feel free to copy ;)

p = argparse.ArgumentParser()
p.add_argument('login', help="Chomikuj login/email")
p.add_argument('password', help="Chomikuj password")
p.add_argument('localUploadDir', help="Path to folder to be uploaded")
p.add_argument('chomikUploadDir', help="Path to folder to be uploaded")
args = p.parse_args()

# logging.basicConfig(
#     level=logging.DEBUG, 
#     format='[%(asctime)s][%(levelname)s]: %(name)s | %(message)s', 
#     datefmt='%H:%M:%S'
#     )

chomik = Chomik(args.login, args.password, requests_session=requests.session())
chomik.login()

localUploadDir = args.localUploadDir
chomikUploadDir = chomik.get_path(args.chomikUploadDir)

print("@"*80)
print("Local Upload Dir: " + localUploadDir)
print("Chomik Upload Dir: " + chomikUploadDir.path)
print("@"*80)


class ProgressCallback(object):
    def __init__(self):
        self.bar = None
        self.stop = True

    def progress_callback(self, par):
        if isinstance(par, ChomikUploader):
            size = par.upload_size
            done = par.bytes_uploaded
        elif isinstance(par, ChomikDownloader):
            size = par.download_size
            done = par.bytes_downloaded

        if self.bar is None:
            self.bar = FileTransferProgressBar(size, par.name)
        self.bar.show(done)

        if done > size / 2 and self.stop:
            print(done)
            self.stop = False
            par.pause()

    def finish_callback(self, par):
        if isinstance(par, ChomikUploader):
            print(par.bytes_uploaded)
        elif isinstance(par, ChomikDownloader):
            print(par.bytes_downloaded)
        self.bar.done()
callback = ProgressCallback()


appDir = os.getcwd()
os.chdir(localUploadDir)

for subdir, dirs, files in os.walk('.'):
    if subdir == '.':
        chomikCurrentDir = chomikUploadDir
    else:
        chomikCurrentDir = chomik.get_path(chomikUploadDir.path + os.path.relpath(subdir))
         
    print("Chomik Current Folder: " + chomikCurrentDir.path)
        
    for d in dirs:
        # Checking if Folder exists on Chomik
        if not isinstance(chomikCurrentDir.get_folder(d), ChomikFolder):
            print(chomikCurrentDir.new_folder(d))
        
    for f in files:
        if not isinstance(chomikCurrentDir.get_file(f), ChomikFile):
            fp = subdir + '/' + f
            up = chomikCurrentDir.upload_file(open(fp, 'rb'), f, callback.progress_callback)
            up.start()
            time.sleep(1)
            if up.paused:
                time.sleep(1)
                up.resume()
            callback.finish_callback(up)

os.chdir(appDir)

chomik.logout()
