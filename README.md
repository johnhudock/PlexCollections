# PlexCollections
Python lib to create Plex collections from IMDB lists

This lets you take a list of IMDB movie lists of the form:
   lists = [['listid1','collection name1'],['listid2','collection name2'],...]
   where the listid's are IMDB movie list ids 'ls########'
and will create a Plex collection on your Plex server, matching movies you have on Plex with the films in the list, so your
Plex collection will basically be an intersection of the movies on your Plex server and the movies in the IMDB list.

The Plex server must be running when you run the script.
You need to update the code to insert your own PLEX_TOKEN. Also update the PLEX_URL, if you are not using the default

I have used it to create many collections without issue. But it might depend 
on your version of Plex and plexapi
If you don't have plexapi: pip install plexapi
fter doing this I started getting warnings about ipykernal. pip install --upgrade ipykernel  fixed it.
developed under python 3.7, Plex server version 4.47.3

Thanks to /u/SwiftPanda16 who provided the python I adapted to make this.
