import os
import spotipy
import logging
from spotipy.oauth2 import SpotifyClientCredentials
from song import Song
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

class SpotifyManager:
    """Class to manage song search queries."""
    def __init__(self) -> None:
        self._sp = self._get_spotify_api_client()

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
        """
        Return a list of audio features of this track, such as valence, acousticness, etc...
        Returns None on failure.
        """
        # audio_features should be a list of dicts. Since we're only searching for 1 track, we only need the first list entry.
        audio_features: list | None = self._sp.audio_features(tracks=[track_uri])
        if not audio_features:
            return None
        return audio_features[0]
    
    def search_song(self, song_name: str, artist_name: str | None = None) -> Song | None:
        """
        Try to search for song_name using the spotify API. 
        Returns a populated Song object or None on failure.
        """
        query = f'{song_name} {artist_name}' if artist_name is not None else song_name
        results = self._sp.search(q=query, limit=1, type='track')
        if not results or not results['tracks']['items']:
            logger.warning(f'search_song({song_name=}): did not get any results!')
            return None
        
        features = self._search_track_features(results['tracks']['items'][0]['uri'])
        if not features:
            logger.warning(f'search_song({song_name=}): did not get song features!')
            return None
        
        song = Song.from_dict_and_features(results, features)
        logger.info(f'search_song({query=}), created song object: {song}')
        return song

# Try it out, test code.
if __name__ == '__main__':
    spotify_manager = SpotifyManager()
    # here's a query that won't work: ASD,A;SDQADXXC
    name = 'Forever Young Blackpink'
    song = spotify_manager.search_song(song_name=name)
