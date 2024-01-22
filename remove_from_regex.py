import os
import re
import time
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from .secrets import *

massive_playlist_url = '3EorBkzySczIQ01Z6TtO2h'
USERNAME = 'yapudjus' # your spotify username
todelete = []

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=YOUR_APP_CLIENT_ID,
                                               client_secret=YOUR_APP_CLIENT_SECRET,
                                               redirect_uri="http://localhost:8080",
                                               scope="user-library-read user-read-private playlist-read-collaborative playlist-modify-public playlist-read-private playlist-modify-private"))

massiveplaylist = sp.user_playlist_tracks(user=USERNAME, playlist_id=massive_playlist_url)
with open('all_data.txt', 'r') as f:
    all_data = f.read().splitlines()
if len(all_data) != massiveplaylist['total']:
    all_data = []
    print('creating all_data variable')
    for j in range(0, int(massiveplaylist['total']), 100):
        try:
            tmp = sp.user_playlist_tracks(user=USERNAME, playlist_id=massive_playlist_url, limit=100, offset=j)
        except:
            print('rate limitted')
            time.sleep(10)
            tmp = sp.user_playlist_tracks(user=USERNAME, playlist_id=massive_playlist_url, limit=100, offset=j)
        for i in tmp['items']:
            if i not in all_data:
                all_data.append(i)
    print(f"all_data variable created {len(all_data)} / {massiveplaylist['total']}")
    os.remove('all_data.txt')
    with open('all_data.txt', 'w') as f:
        for i in all_data:
            f.write(str(i) + '\n')
else:
    print('loading cached all_data variable')
    new_all_data = []
    for i in all_data:
        new_all_data.append(eval(i))
    all_data = new_all_data
    del new_all_data

# all_data = []
# print('creating all_data variable')
# for j in range(0, int(massiveplaylist['total']), 100):
#     try:
#         tmp = sp.user_playlist_tracks(user=USERNAME, playlist_id=massive_playlist_url, limit=100, offset=j)
#     except:
#         print('rate limitted')
#         time.sleep(10)
#         tmp = sp.user_playlist_tracks(user=USERNAME, playlist_id=massive_playlist_url, limit=100, offset=j)
#     for i in tmp['items']:
#         if i not in all_data:
#             all_data.append(i)


regex = input('regex: ')
matchon = input('match on (0:album | 1:name | 2:both | 3:artist): ')

if matchon == '0':
    for i in all_data:
        if re.search(regex, i['track']['album']['name'], re.IGNORECASE):
            todelete.append(i)
elif matchon == '1':
    for i in all_data:
        if re.search(regex, i['track']['name'], re.IGNORECASE):
            todelete.append(i)
elif matchon == '2':
    n = 0
    for i in all_data:
        n += 1
        print(n)
        if re.search(r'.*remastered.*', i['track']['name'], re.IGNORECASE) or re.search(r'.*remastered.*', i['track']['album']['name'], re.IGNORECASE):
            todelete.append(i)
elif matchon == '3':
    for i in all_data:
        for tmp in i['track']['artists']:
            if re.search(regex, tmp['name'], re.IGNORECASE):
                todelete.append(i)

deletebatch = []
for i in todelete:
    print(f"delete {i['track']['name']} - {i['track']['album']['name']} - {[j['name'] for j in i['track']['artists']]}")
    deletebatch.append(i['track']['id'])
    if len(deletebatch) == 100:
        sp.user_playlist_remove_all_occurrences_of_tracks(user=USERNAME, playlist_id=massive_playlist_url, tracks=deletebatch)
        deletebatch = []
if len(deletebatch) > 0:
    sp.user_playlist_remove_all_occurrences_of_tracks(user=USERNAME, playlist_id=massive_playlist_url, tracks=deletebatch)