import os
import spotipy
import json
from spotipy.oauth2 import SpotifyClientCredentials
from song import Song

class SpotifyManager:
    def __init__(self) -> None:
        self.sp = self._get_spotify_api_client()

    @staticmethod
    def _load_spotify_credentials(filename: str) -> tuple[str, str]:
        """
        Extract client_id, client_secret Spotify API credentials from the specified file.
        Load them into environment variables as SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET.
        """
        with open(filename, 'r') as f:
            client_id, client_secret = f.read().strip().split()
            os.environ['SPOTIPY_CLIENT_ID'] = client_id
            os.environ['SPOTIPY_CLIENT_SECRET'] = client_secret

    def _get_spotify_api_client(self) -> spotipy.Spotify:
        """
        Return an initialized and authenticated Spotify object, ready for searches and API calls.
        """
        self._load_spotify_credentials('spotify_credentials.txt')
        client_credentials_mananger = SpotifyClientCredentials()
        spotify = spotipy.Spotify(auth_manager=client_credentials_mananger)
        return spotify
    
    def _search_track_features(self, track_uri: str) -> list | None:
        # audio_features should be a list of dicts. Since we're only searching for 1 track, we only need the first list entry.
        audio_features: list | None = self.sp.audio_features(tracks=[track_uri])
        print(f'{type(audio_features) = }, {json.dumps(audio_features, indent=4)}\n\n')
        return audio_features[0]

    
    def search_song(self, song_name: str) -> Song | None:
        results = self.sp.search(q=song_name, limit=1, type='track')
        if not results:
            return None
        
        features = self._search_track_features(results['tracks']['items'][0]['uri'])
        if not features:
            return None
        
        song = Song.from_dict_and_features(results, features)
        return song
    
if __name__ == '__main__':
    spotify_manager = SpotifyManager()
    song_name = 'Forever Young Blackpink'
    song = spotify_manager.search_song(song_name=song_name)
    print(f'{type(song) = }')
    print(f'results for {song_name = }, {song} ')
    # with open('example_song_search.json', 'w') as f:
    #     json.dump(results, f, indent=4)
    # print(json.dumps(results, indent=4))
