from __future__ import annotations
from dataclasses import dataclass

@dataclass()
class Song:
    artist_name: str
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
    def from_dict_and_features(cls, d: dict, features: list[str]) -> Song:
        items: dict = d['tracks']['items'][0]
        return cls(
            artist_name=items['artists'][0]['name'],
            image_url=cls._parse_image_url(items['album']['images']),
            song_name=items['name'],
            track_href=items['external_urls']['spotify'],
            track_uri=items['uri'],
            danceability=features[]
        )
    
    @staticmethod
    def _parse_image_url(images: dict) -> str:
        """
        Get the URL to the image. Tries to get a medium resolution.
        """
        # images are provided in highest resolution first order.
        if len(images) == 1:
            return images[0]['url']
        return images[-2]['url']
    
    def get_features():
        pass