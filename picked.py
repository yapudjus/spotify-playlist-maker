import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from .secrets import *

toadd = []

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=YOUR_APP_CLIENT_ID,
                                                client_secret=YOUR_APP_CLIENT_SECRET,
                                                redirect_uri=SPOTIPY_REDIRECT_URI,
                                                scope="user-library-read user-read-private playlist-read-collaborative playlist-modify-public playlist-read-private playlist-modify-private"))

with open('playlists.txt', 'r') as f:
    for line in f:
        toadd.append(line.strip())

result = sp.search(q='music picked just for you', type='playlist', limit=50)
n=0
for i in range(0, int(result['playlists']['total']), 50):
    n+=1
    result = sp.search(q='music picked just for you', type='playlist', limit=50, offset=i)
    for playlist in result['playlists']['items']:
        if (playlist['description'].find('picked for you') != -1) or (playlist['name'].find('music') != -1) and (playlist['owner']['display_name'] == 'Spotify'):
            if playlist['id'] not in toadd:
                toadd.append(playlist['id'])
                print(f"adding {playlist['name']} {n}/{int(result['playlists']['total']/50)}")
                with open('playlists.txt', 'a') as f:
                    f.write(playlist['id'] + '\n')
    print(f"{n}/{int(result['playlists']['total']/50)}")
    time.sleep(2)

for i in toadd:
    print(f"{i['name']} - {i['owner']['display_name']} - {i['description']}")
