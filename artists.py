import os
import time
import sqlite3
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from .secrets import *
USERNAME = 'yapudjus' # your spotify username

artists = []
with open('/root/spotify_massive_playlist/artists.txt', 'r') as f:
    for line in f.readlines() :
        artists.append(list(line.strip().split(', ')))

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=YOUR_APP_CLIENT_ID,
                                    client_secret=YOUR_APP_CLIENT_SECRET,
                                    redirect_uri=SPOTIPY_REDIRECT_URI,
                                    scope="user-library-read user-read-private playlist-read-collaborative playlist-modify-public playlist-read-private playlist-modify-private"))


for artist in artists :
    # get artist full discography in order
    artist_tracks = []
    albums = []
    response = sp.artist_albums(artist[0])
    while response["next"] != None :
        for i in response["items"]:
            albums.append(i)
        response = sp.next(response)
    for i in response["items"]:
        albums.append(i)
    
    albums = sorted(albums, key=lambda x: x['release_date'], reverse=True)
    for album in albums :
        response = sp.album_tracks(album['id'])
        while response["next"] != None :
            for i in response["items"]:
                if str(i["artists"]).find(artist[0]) != -1:
                    artist_tracks.append(i["id"])
            response = sp.next(response)
        for i in response["items"]:
            if str(i["artists"]).find(artist[0]) != -1:
                artist_tracks.append(i)
    

    # create playlist
    playlist_id = artist[1]
    print('Clearing playlist...')
    tmp1 = sp.user_playlist_tracks(user=USERNAME, playlist_id=playlist_id)
    tmp2 = []
    for j in range(0, int(tmp1['total']), 100):
        try:
            tmp = sp.user_playlist_tracks(user=USERNAME, playlist_id=playlist_id, limit=100, offset=j)
        except:
            print('rate limitted')
            time.sleep(10)
            tmp = sp.user_playlist_tracks(user=USERNAME, playlist_id=playlist_id, limit=100, offset=j)
        for i in tmp['items']:
            if i['track']['id'] not in tmp2:
                tmp2.append(i['track']['id'])
    for i in tmp2:
        sp.user_playlist_remove_all_occurrences_of_tracks(user=USERNAME, playlist_id=playlist_id, tracks=[i])
    print('Done!')
    for i in range(0, len(artist_tracks), 10) :
        print(i)
        tmplist = []
        for j in range(i, i+10) :
            if j < len(artist_tracks) :
                tmplist.append(artist_tracks[j]['id'])
        sp.user_playlist_add_tracks(USERNAME, playlist_id, tmplist)
        time.sleep(2)