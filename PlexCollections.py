# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 14:03:07 2021

@author: john
"""
#------------------------------------------------------------------------------
#		Script to create Plex Collections from IMDB lists.
#
#		Adapted from:
#       Automated IMDB Top 250 Plex collection script by /u/SwiftPanda16
#
#                         *** Use at your own risk! ***
#   *** I am not responsible for damages to your Plex server or libraries. ***
#	
#    I have used it to create many collections without issue. But it might depend 
#    on your version of Plex and plexapi
#    If you don't have plexapi: pip install plexapi
#    after doing this I started getting warnings about ipykernal. pip install --upgrade ipykernel  fixed it.
#	 developed under python 3.7, Plex server version 4.47.3
#
#------------------------------------------------------------------------------

import json
import requests
import time
from plexapi.server import PlexServer
import pandas as pd

### Plex server details ###
PLEX_URL = 'http://localhost:32400'
PLEX_TOKEN = 'xxxxxxxxxxxx'

### Existing movie library details ###
MOVIE_LIBRARIES = ['Movies']

### New IMDB Top 250 library details ###
IMDB_CHART_URL = 'http://www.imdb.com/chart/top'

### The Movie Database details ###
# Enter your TMDb API key if your movie library is using "The Movie Database" agent.
# This will be used to convert the TMDb IDs to IMDB IDs.
# You can leave this blank '' if your movie library is using the "Plex Movie" agent.
TMDB_API_KEY = ''


##### CODE BELOW #####

TMDB_REQUEST_COUNT = 0  # DO NOT CHANGE

def add_collection(library_key, rating_key, collection_name):
    headers = {"X-Plex-Token": PLEX_TOKEN}
    params = {"type": 1,
              "id": rating_key,
              "collection[0].tag.tag": collection_name,
              "collection.locked": 1
              }

    url = "{base_url}/library/sections/{library}/all".format(base_url=PLEX_URL, library=library_key)
    r = requests.put(url, headers=headers, params=params)


def remove_from_collection(library_key, rating_key, collection_name):
    headers = {"X-Plex-Token": PLEX_TOKEN}
    params = {"type": 1,
              "id": rating_key,
              "collection[].tag.tag-": collection_name
              }

    url = "{base_url}/library/sections/{library}/all".format(base_url=PLEX_URL, library=library_key)
    r = requests.put(url, headers=headers, params=params)

def delete_collection(collection_name,server):
    print(f'deleteing collection {collection_name}')
    try:
        server.library.search(collection_name, libtype='collection')[0].delete()
    except:
        print('Couldnt delete')


def get_imdb_id_from_tmdb(tmdb_id):
    global TMDB_REQUEST_COUNT
    
    if not TMDB_API_KEY:
        return None
    
    # Wait 10 seconds for the TMDb rate limit
    if TMDB_REQUEST_COUNT >= 40:
        time.sleep(10)
        TMDB_REQUEST_COUNT = 0
    
    params = {"api_key": TMDB_API_KEY}
    
    url = "https://api.themoviedb.org/3/movie/{tmdb_id}".format(tmdb_id=tmdb_id)
    r = requests.get(url, params=params)
    
    TMDB_REQUEST_COUNT += 1
    
    if r.status_code == 200:
        movie = json.loads(r.text)
        return movie['imdb_id']
    else:
        return None
    
def getIMDBList(listid,listname):
    url = f'https://www.imdb.com/list/{listid}/export?ref_=ttls_otexp'
    l=pd.read_csv(url,encoding = 'latin1')
    l=l[l['Year'].notnull()].drop_duplicates()
    l['IMDB']=l['URL'].str.slice(27,36)
    list = l[['IMDB','Title', 'Year', 'IMDb Rating', 'Directors', 'Genres']].copy()
    list['ListName'] = listname
    list['ListLinks'] = f'https://www.imdb.com/list/{listid}/'
    list.set_index('ListName',inplace=True)
    return list
	
def getPLEXMovies(movielib):
    try:
        plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    except:
        print("No Plex server found at: {base_url}".format(base_url=PLEX_URL))
        print("Exiting script.")
        return [], 0

    # Get list of movies from the Plex server
    all_movies = []
    movie_lib=movielib
    try:
        print("Retrieving a list of movies from the '{library}' library in Plex...".format(library=movie_lib))
        movie_library = plex.library.section(movie_lib)
        library_language = movie_library.language  # IMDB will use language from last library in list
        all_movies.extend(movie_library.all())
    except:
        print("The '{library}' library does not exist in Plex.".format(library=movie_lib))
        print("Exiting script.")
        return []
    return plex, all_movies
    

def createListCollections(server, movies, movielists):
    imlists=[]
    for li in movielists:
        print(li[0],li[1])
        try:
            list = getIMDBList(li[0],li[1])
            imlists.append(list)
            delete_collection(li[1],server)
        except:
            print('Couldnt get list ',li[0],':',li[1])
    
   
    for m in movies:
        if 'imdb://' in m.guid:
            imdb_id = m.guid.split('imdb://')[1].split('?')[0]
        elif 'themoviedb://' in m.guid:
            tmdb_id = m.guid.split('themoviedb://')[1].split('?')[0]
            imdb_id = get_imdb_id_from_tmdb(tmdb_id)
        else:
            imdb_id = None
            
        if imdb_id:
            lno = 0
            for list in imlists:
                listname = movielists[lno][1]
                if (list.IMDB==imdb_id).any():
                    add_collection(m.librarySectionID, m.ratingKey, listname)
                lno=lno+1
       
        


if __name__ == "__main__":
    
    plexserver,movies = plex.getPLEXMovies('Movies')
    
    # Add or remove additional IMDB lists below [istid, listname],
    lists=[['ls069008658','AFI Greatest Movie Nominees'],
           ['ls058705802','NY Times Top 1000 '],
           ['ls021251975','AFI Greatest Musicals']]
    
    plex.createListCollections(plexserver,movies,lists)
