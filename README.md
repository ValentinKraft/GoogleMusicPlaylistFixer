# GoogleMusicPlaylistFixer

**Description:**

This little program fixes some issues I came across when using the Google Play Music Manager to upload my iTunes playlists. I use Google Play Music for an online-version of my local iTunes media library. The Music Manager offers some functionality to upload and transfer your iTunes playlists to Google Play Music. Unfortunately the Music Manager messed up the playlists, always adding entries to the playlists which resulted in huge playlists containing a lot of duplicates of the songs.

The Playlist Fixer fixes this issues using a brute force approach: deleting the contents of every playlist and again adding all entries. To get access to Google Play Music, the Playlist Fixer uses the gmusicapi from Simon Weber (https://github.com/simon-weber/gmusicapi). To export the local iTunes playlists I used the iTunes Export program by Eric Daugherty (http://www.ericdaugherty.com/dev/itunesexport/).

Please note that this is just a hobby project and I won’t take any responsibility for possible damage of your hard- or software. Furthermore this is still a work in progress and will be further developed in the future.

**How to install:**
- Install python 3.X
- Install Java Runtime Environment
- Run command line and type in:
```
pip install gmusicapi
pip install colorama
```

- Copy the files of the PlaylistFixer to C:\GoogleMusicPlaylistFixer\
- Open the PlaylistFixer.py file with your editor and type in your Google Account details (Your E-Mail and Password) to the line „logged_in = api.login(„YourEmail“, „YourPassword“, Mobileclient.FROM_MAC_ADDRESS)“. Save the file.

**How to use:**

The PlaylistFixer just tries to fix the playlist and won’t upload any files (yet). Therefore the steps to fix your playlists are:
- Use the official Google Play Music Manager to upload your MP3 music library to Google Music so that the MP3 files in your playlists are already on the Google servers (But turn off the Auto-Start function, just use the Music Manager to upload your media library).
- In Google Play Music, for every iTunes playlist you want to upload, create a playlist in Google Music with the same name
  - Important!: Note that all special characters (like „*“, „!“, etc.) in your iTunes playlist names will be converted to „\_“. Therefore the names of your Google Music playlists should have „\_“ instead of the special characters in your iTunes playlist names. You just have to do this once.
- Temporarily turn off the synchronisation on all your devices running the Google Play Music App (most likely your smartphone) (otherwise the app will delete your offline MP3s and you re-download all of your music).
- Now run the PlaylistFixer with opening the command line and type in:
```
Python C:\GoogleMusicPlaylistFixer\PlaylistFixer.py
```
- The PlaylistFixer will now fill all Google Music playlists he can assign to one of your iTunes playlists with the right tracks.

*For more information visit www.valentinkraft.de*
