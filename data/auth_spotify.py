# auth_spotify.py

import requests
import base64
import time
import config

TOKEN_URL = "https://accounts.spotify.com/api/token"

class SpotifyAuth:
    def __init__(self):
        self.token = None
        self.token_expires = 0

    def get_token(self):
        current_time = time.time()
        if self.token is None or self.token_expires < current_time:
            self.token = self.request_new_token()
            self.token_expires = current_time + 3600  # Token valide pendant 1 heure
        return self.token

    def request_new_token(self):
        auth_header = base64.b64encode(f"{config.CLIENT_ID}:{config.CLIENT_SECRET}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_header}",
        }
        data = {
            "grant_type": "client_credentials"
        }
        response = requests.post(TOKEN_URL, headers=headers, data=data)
        if response.status_code == 200:
            token_info = response.json()
            return token_info["access_token"]
        else:
            raise Exception("Failed to get Spotify token")

spotify_auth = SpotifyAuth()
