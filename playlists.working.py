import os
import time
import pytz
import sqlite3
import spotipy
from datetime import datetime
from spotipy.oauth2 import SpotifyOAuth
#from bottle import route, run, request
from flask import Flask, redirect, request, session
import requests

from .secrets import *

USERNAME = 'yapudjus' # replace with your username
massive_playlist_url = '6vs4RS6ym9ZUaS94xF5NIE' # replace with id of your main recom playlist
weekly_playlist_url = '7d53DJlLUdue5S1smf9FoV' # replace with id of your weekly recom playlist
daily_playlist_url = '2XjccH3rJfbvdeCgPwSvys' # replace with id of your daily recom playlist

toadd = []
db = sqlite3.connect('./spotify.db') # schema is CREATE TABLE history (id INTEGER primary key, playlist_id INTEGER, track_id INTEGER, date TEXT);
def check_db(playlist_id, track_id, date=time.strftime("%Y-%m-%d")):
    result = db.execute("SELECT * FROM history WHERE playlist_id = ? AND track_id = ? AND date = ?", (playlist_id, track_id, date))
    result = result.fetchall()
    if result:
        print(f"{track_id} in playlist {playlist_id} already in DB")
        return True
    else:
        print(f"{track_id} in playlist {playlist_id} not in DB")
        return False

def add_to_db(playlist_id, track_id):
    db.execute("INSERT INTO history VALUES (NULL, ?, ?, ?)", (playlist_id, track_id, time.strftime("%Y-%m-%d")))
    db.commit()

app = Flask(__name__)
app.secret_key = "k16seth861ezg51qenzqr186zge35g2z8nycqzt(7y54s1g7q5eGR5h42QSZqz54S5gzf"
sp_oauth=SpotifyOAuth(client_id=YOUR_APP_CLIENT_ID,
                                    client_secret=YOUR_APP_CLIENT_SECRET,
                                    redirect_uri=SPOTIPY_CLIENT_SECRET,
                                    scope="user-library-read user-read-private playlist-read-collaborative playlist-modify-public playlist-read-private playlist-modify-private", cache_path="./.cache")
# sp_oauth = oauth2.SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI,scope=SCOPE,cache_path=CACHE )
# sp = spotipy.Spotify(auth_manager=sp_oauth)

@app.route("/login")
def login():
    auth_url = sp_oauth.get_authorize_url()
    session["token_info"] = sp_oauth.get_cached_token()
    return redirect(auth_url)
@app.route("/callback")
def callback():
    token_info = sp_oauth.get_access_token(request.args["code"])
    session["token_info"] = token_info
    print(token_info)
    return redirect("/generate")  # Redirect to app's main page
# context = ('server.crt', 'server.key')#certificate and key files
# app.run('m.yapudjusowndomain.fr', '7654')

sp = spotipy.Spotify(auth_manager=sp_oauth)


print('Getting playlist...')
with open('./playlists.txt', 'r') as f:
    for line in f:
        if line != '\n':
            toadd.append(line.strip())
        toadd.append(line.strip())
print('Done!')

#clear daily playlist
if datetime.now(pytz.timezone('europe/paris')).strftime("%H") == '00':
    print('Clearing daily playlist...')
    dailytracks = sp.user_playlist_tracks(user=USERNAME, playlist_id=daily_playlist_url)
    all_daily = []
    print('creating all_daily variable')
    for j in range(0, int(dailytracks['total']), 100):
        try:
            tmp = sp.user_playlist_tracks(user=USERNAME, playlist_id=daily_playlist_url, limit=100, offset=j)
        except:
            print('rate limitted')
            time.sleep(10)
            tmp = sp.user_playlist_tracks(user=USERNAME, playlist_id=daily_playlist_url, limit=100, offset=j)
        for i in tmp['items']:
            if i['track']['id'] not in all_daily:
                all_daily.append(i['track']['id'])
    for i in all_daily:
        sp.user_playlist_remove_all_occurrences_of_tracks(user=USERNAME, playlist_id=daily_playlist_url, tracks=[i])
    print('Done!')
    if datetime.now(pytz.timezone('europe/paris')).weekday() == 4 :
        print('Clearing weekly playlist...')
        weeklytracks = sp.user_playlist_tracks(user=USERNAME, playlist_id=weekly_playlist_url)
        all_weekly = []
        print('creating all_weekly variable')
        for j in range(0, int(weeklytracks['total']), 100):
            try:
                tmp = sp.user_playlist_tracks(user=USERNAME, playlist_id=weekly_playlist_url, limit=100, offset=j)
            except:
                print('rate limitted')
                time.sleep(10)
                tmp = sp.user_playlist_tracks(user=USERNAME, playlist_id=weekly_playlist_url, limit=100, offset=j)
            for i in tmp['items']:
                if i['track']['id'] not in all_daily:
                    all_weekly.append(i['track']['id'])
        for i in all_weekly:
            sp.user_playlist_remove_all_occurrences_of_tracks(user=USERNAME, playlist_id=weekly_playlist_url, tracks=[i])
        print('Done!')

massiveplaylist = sp.user_playlist_tracks(playlist_id=massive_playlist_url)
with open('./all_ids.txt', 'r') as f:
    all_ids = f.read().splitlines()
if len(all_ids) != massiveplaylist['total']:
    all_ids = []
    print('creating all_ids variable')
    for j in range(0, int(massiveplaylist['total']), 100):
        try:
            tmp = sp.user_playlist_tracks(user=USERNAME, playlist_id=massive_playlist_url, limit=100, offset=j)
        except:
            print('rate limitted')
            time.sleep(10)
            tmp = sp.user_playlist_tracks(user=USERNAME, playlist_id=massive_playlist_url, limit=100, offset=j)
        for i in tmp['items']:
            if i['track']['id'] not in all_ids:
                all_ids.append(i['track']['id'])
    print(f"all_ids variable created {len(all_ids)} / {massiveplaylist['total']}")
    os.remove('./all_ids.txt')
    with open('./all_ids.txt', 'w') as f:
        for i in all_ids:
            f.write(i + '\n')
else:
    print('using cached all_ids variable')

n=0
for i in toadd:
    n+=1
    print(i)
    try:
        playlist_tracks = sp.user_playlist_tracks(user=USERNAME, playlist_id=i)
    except:
        print('rate limitted')
        time.sleep(10)
        playlist_tracks = sp.user_playlist_tracks(user=USERNAME, playlist_id=i)
    tracks = []
    all_ids_to_add = []
    for track in playlist_tracks['items']:
        if check_db(i, track['track']['id']) == False:
            add_to_db(i, track['track']['id'])
        if (track['track']['id'] not in all_ids):
            tracks.append(track['track']['id'])
            all_ids.append(track['track']['id'])
            all_ids_to_add.append(track['track']['id'])
            print(f"adding |{track['track']['name']}| in playlists")
    print(f'{n}/{len(toadd)}')
    if len(tracks) > 0:
        try:
            sp.user_playlist_add_tracks(playlist_id=massive_playlist_url, tracks=tracks, user=USERNAME, position=None)
            sp.user_playlist_add_tracks(playlist_id=daily_playlist_url, tracks=tracks, user=USERNAME, position=None)
            sp.user_playlist_add_tracks(playlist_id=weekly_playlist_url, tracks=tracks, user=USERNAME, position=None)
        except:
            print('rate limitted')
            time.sleep(5)
            try:
                sp.user_playlist_add_tracks(playlist_id=massive_playlist_url, tracks=tracks, user=USERNAME, position=None)
                sp.user_playlist_add_tracks(playlist_id=daily_playlist_url, tracks=tracks, user=USERNAME, position=None)
                sp.user_playlist_add_tracks(playlist_id=weekly_playlist_url, tracks=tracks, user=USERNAME, position=None)
            except: 
                print('unk_err')
        with open('./all_ids.txt', 'a') as f:
            for er in all_ids_to_add :f.write(er)
