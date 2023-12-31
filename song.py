from __future__ import annotations

import json
import logging
from dataclasses import dataclass, asdict
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger()

@dataclass
class Song:
    """Represents a song and its music features, obtained from the Spotify API."""
    artist_name: str
    album_name: str
    album_url: str
    image_url: str
    song_name: str
    track_href: str
    track_uri: str
    danceability: float
    energy: float
    key: int
    loudness: float
    mode: int
    speechiness: float
    acousticness: float
    instrumentalness: float
    liveness: float
    valence: float
    tempo: float

    @classmethod
    def from_dict_and_features(cls, d: dict, features: list[str]) -> Song | None:
        try:
            items: dict = d['tracks']['items'][0]
            return cls(
                artist_name=items['artists'][0]['name'],
                album_name=items['album']['name'],
                album_url=items['album']['external_urls']['spotify'],
                image_url=cls._parse_image_url(items['album']['images']),
                song_name=items['name'],
                track_href=items['external_urls']['spotify'],
                track_uri=items['uri'],
                danceability=features['danceability'],
                energy=features['energy'],
                key=features['key'],
                loudness=features['loudness'],
                mode=features['mode'],
                speechiness=features['speechiness'],
                acousticness=features['acousticness'],
                instrumentalness=features['instrumentalness'],
                liveness=features['liveness'],
                valence=features['valence'],
                tempo=features['tempo']
            )
        except Exception as e:
            logging.error(f'Failed to create Song object: {e}')
            return None
    
    def __str__(self) -> str:
        """
        Returns a json formatted representation of this song.
        """
        return json.dumps(asdict(self), indent=4)

    @staticmethod
    def _parse_image_url(images: dict) -> str:
        """
        Get the URL to the image. Tries to get a medium resolution.
        """
        # images are provided in highest resolution first order.
        if len(images) == 1:
            return images[0]['url']
        return images[-2]['url']
    
    def get_features(self, feature_names: list[str]) -> list[float]:
        """
        Extract the specified features from the Song object and return them as a list.

        Args:
            feature_names (list[str]): List of feature names (like ['danceability', 'energy'])

        Returns:
            list[float]: List of the values of the specified features.
        """
        song_as_dict = asdict(self)
        feature_values = [song_as_dict[feature] for feature in feature_names]
        return feature_values
    
    def get_features_to_create_df_entry(self) -> list:
        """
        Returns a list of features to allow this song to be added to the data.csv dataframe.
        Will be a list of various types.
        """
        return [
            self.valence,
            None, # don't have 'year'
            self.acousticness,
            f"['{self.artist_name}']", # 'artists', we only have 1.
            self.danceability,
            None, # don't have 'duration_ms' (it's in the api return but don't need it.)
            self.energy,
            None, # don't have 'explicit', doesn't matter though
            None, # don't have 'id'
            self.instrumentalness,
            self.key,
            self.liveness,
            self.loudness,
            self.mode,
            self.song_name,
            None, # don't have 'popularity'
            None, # don't have 'release_date',
            self.speechiness,
            self.tempo
        ]

    
    def to_dict(self) -> dict:
        return asdict(self)
    