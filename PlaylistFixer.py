#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals
from future import standard_library
standard_library.install_aliases()
from builtins import *  # noqa
from getpass import getpass

from gmusicapi import Mobileclient

import os
import sys
import colorama
import datetime
from subprocess import check_call
from mutagen.mp3 import EasyMP3 as MP3
from os.path import expanduser
from colorama import Fore, Back, Style

# ///////////////// Helper classes /////////////////
# //////////////////////////////////////////////////

class Tee(object):
    def __init__(self, log_fname, mode='a'):
        self.log = open(log_fname, mode)

    def __del__(self):
        # Restore sin, so, se
        sys.stdout = sys.__stdout__
        sys.stdir = sys.__stdin__
        sys.stderr = sys.__stderr__
        self.log.close()

    def write(self, data):
        self.log.write(data)
        self.log.flush()
        sys.__stdout__.write(data)
        sys.__stdout__.flush()

    def readline(self):
        s = sys.__stdin__.readline()
        sys.__stdin__.flush()
        self.log.write(s)
        self.log.flush()
        return s

    def flush(foo):
        return

# //////////////// Helper functions ////////////////
# //////////////////////////////////////////////////

def init_logger():
    sys.stdout = sys.stderr = sys.stdin = Tee("log"+str(datetime.datetime.now().time()).replace(":","_")+".txt", 'w')

def end_logger():
    sys.stdout = sys.__stdout__

def ask_for_credentials():
    """Make an instance of the api and attempts to login with it.
    Returns the authenticated api.
    """

    # We're not going to upload anything, so the Mobileclient is what we want.
    api = Mobileclient(debug_logging=False)

    logged_in = False
    attempts = 0

    #try:
    #    logged_in = api.login("mail", "pass", Mobileclient.FROM_MAC_ADDRESS)
    #except:
    #    print(Fore.YELLOW + "Error logging you in!")

    while not logged_in and attempts < 3:
        print("Please log in into your Google Play account.")
        email = input('Email: ')
        password = getpass()

        logged_in = api.login(email, password, Mobileclient.FROM_MAC_ADDRESS)
        attempts += 1

    return api

def load_local_playlist(filepath):
    """Loads the playlist file in the given directory, giving back a list of MP3 file paths."""
    mp3List = list()
    file = open(filepath, encoding="utf-8", mode='r')
    for line in file:
        line = line.replace('\\','/').strip()
        if os.path.exists(line):
            mp3List.append(line)
        #else:
        #    print("Couldn't locate " + line + " in " + filepath)

    if len(mp3List)==0:
        print(Fore.RED + "~~ ERROR Corrupt playlist file! " + filepath)

    return mp3List

def export_itunes_playlists(exportPath):
    print("Calling iTunesExport ...")
    print("-----------------------------------------------------")
    try:
        #check_call(['java', '-jar', 'C:\GoogleMusicPlaylistFixer\iTunesExport\itunesexport.jar', "-outputDir="+exportPath])
        check_call(['java', '-jar', 'C:\Coding\!PROJECTS\GoogleMusicPlaylistFixer\iTunesExport\itunesexport.jar', "-outputDir="+exportPath])
    except:
        print("Problem exporting iTunes Playlists! Please install iTunesExport Console from http://www.ericdaugherty.com/dev/itunesexport/")
    print("-----------------------------------------------------")

def give_track_id(artist, title, album):
    """Gives the ID of the (last) track matching the given artists and song title. Returns 0 if no ID is found."""
    id = "0"
    for song in library:
        #print (song['durationmillis'])
        if (song['title'] == title and song['artist'] == artist) or (song['title'] == title and song['album'] == album):
            id = song['id']
    return id

def give_playlist_id(name):
    """Gives the ID of the (last) playlist matching the given name. Returns 0 if no ID is found."""
    id = "0"
    for pl in playlistsContent:
        if pl['name'] == name:
            id = pl['id']
    return id

def clear_all_playlists():
    """Deletes the content of every Google Music playlist."""
    for pl in playlistsContent:
        trackList=list()
        for track in pl['tracks']:
            trackList.append(track['id'])
        mc.remove_entries_from_playlist(trackList)

def fill_playlists():
    """Appends the tracks to the right playlists based on the local playlist files. Assumes empty Google Music playlists. Fills only already existing Google Music playlists, doesn't create new playlists."""
    i = 0
    for pl in localPlaylists:

        plID = give_playlist_id(localPlaylistNames[i])
        if plID == "0":
                print(Fore.YELLOW + "~~ Couldn't get ID for Playlist " + localPlaylistNames[i] + " - skipping")
                i=i+1
                continue

        print("--------------------------------------------")
        print("/// Processing Playlist " + localPlaylistNames[i])
        ids=list()

        for song in pl:
            try:
                id3info = MP3(song)
            except:
                print(Fore.YELLOW + "~~ ERROR reading ID3 tag for " + song + " - skipping")
                continue
            #print(id3info['length'])
            try:
                try:
                    artist = id3info['artist'][0]
                except:
                    artist = ""
                try:
                    title = id3info['title'][0]
                except:
                    title = ""
                try:
                    album = id3info['album'][0]
                except:
                    album = ""
                id = give_track_id(artist,title,album)
            except:
                print(Fore.YELLOW + "~~ ERROR retreaving Google Music ID for " + song + " - skipping")
                continue
            if len(ids) >= 1000:
                print(Fore.YELLOW + "Playlist has more than 1000 songs - skipping the rest")
                break
            if id == "0":
                print(Fore.YELLOW + "~~ ERROR retreaving Google Music ID for " + song + " - skipping")
                continue
            else:
                ids.append(id)
            
        mc.add_songs_to_playlist(plID, ids)
        i=i+1
        print("Done.")
        print()

def ask_user_to_proceed(exportPath):
    
    while True:
        print(Fore.RED + 'The content of your online playlists is about to be deleted. They will be replaced by the files in ' + exportPath + ".\n Please check if the names of the playlists in the directory match the online playlists.") 
        answer = input('Proceed? (Y/N)')
        print()
        if(answer == "Y" or answer == "y" or answer == "Yes" or answer == "yes"):
            return True
        if(answer == "N" or answer == "n" or answer == "No" or answer == "no"):
            return False


# //////////////////////////////////////////////////
# //////////////////////////////////////////////////

def main():
    """Fixes the Google Music playlists if they differ from the local iTunes playlists."""

    colorama.init(autoreset=True)

    print()
    print(Style.BRIGHT + '##########################################################')
    print(Style.BRIGHT + "############# GoogleMusic PlaylistFixer V0.1 #############")
    print(Style.BRIGHT + '##########################################################')
    print("(c) 2016 by Valentin Kraft, www.valentinkraft.de")
    print()

    # Start mobile client / Initialization
    global mc
    mc = ask_for_credentials()
    init_logger()
    colorama.init(autoreset=True)
    if not mc.is_authenticated():
        print("Sorry, those credentials weren't accepted.")
        return
    print('Successfully logged in.')
    print()

    # Scanning local media
    print(Style.BRIGHT + "/// Scanning local iTunes playlists. //////////////")
    print(Style.BRIGHT + '///////////////////////////////////////////////////')
   
    global localPlaylists
    localPlaylists=list()
    global localPlaylistNames
    localPlaylistNames=list()

    userPath = expanduser("~")
    exportPath = userPath + "\\GoogleMusicPlaylistFixerExport"

    export_itunes_playlists(exportPath)

    for file in os.listdir(exportPath):
        localPlaylists.append(load_local_playlist(exportPath+"\\"+file))
        localPlaylistNames.append(file.split(".")[0])
    print(Fore.GREEN + "Done. Sucessfully processed " + str(len(localPlaylists)) + " iTunes playlists.")
    print()

    # Scanning Google Music playlists
    print(Style.BRIGHT + "/// Scanning Google Music playlists. //////////////")
    print(Style.BRIGHT + '///////////////////////////////////////////////////')
    print('Loading library... Please wait!')
    
    global library
    library = mc.get_all_songs()
    global playlists
    playlists = mc.get_all_playlists()
    global playlistsContent
    playlistsContent = mc.get_all_user_playlist_contents()

    print(Fore.GREEN + 'Done.')
    print()

    # Consistency check
    if len(library) == 0 or len(playlists) == 0 or len(playlistsContent) == 0 or len(localPlaylists) == 0:
        print(Fore.RED + "~~ ERROR retrieving Google Music library data - Aborting")
        return

    # Ask user for permission
    proceed = ask_user_to_proceed(exportPath)
    if(proceed == False):
        print("Aborting.")
        return
                
    # Fix Google Music library
    print(Style.BRIGHT + "/// Fixing library. ///////////////////////////////")
    print(Style.BRIGHT + '///////////////////////////////////////////////////')
    clear_all_playlists()
    fill_playlists()
   
    #TODO: delete m3u files?

    # End
    mc.logout()
    end_logger()
    print()
    print(Fore.LIGHTGREEN_EX + '___________ Finished!')
    print()


if __name__ == '__main__':
    main()
