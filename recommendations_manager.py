import ast
import logging
import json
import numpy as np
import pandas as pd
from typing import Type
from sklearn.preprocessing import MinMaxScaler
from spotify_manager import SpotifyManager
from models.my_k_neighbors_classifier import MyKNeighborsClassifier
from models.gpu_kneighbors import GpuKNeighbors
from models.knn_song_classifier import KnnSongClassifier
from models.distance_metric import DistanceMetric
from logging_config import setup_logging
from song import Song

DATA_FEATURES = ['valence', 'acousticness', 'danceability', 'energy', 
                 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo']

setup_logging()
logger = logging.getLogger(__name__)

class RecommendationsManager:
    """Class to handle getting song recommendations given an input song."""
    def __init__(
            self, 
            data: pd.DataFrame, 
            features: list[str], 
            spotify_manager: SpotifyManager, 
            classifier: Type[KnnSongClassifier], 
            dist_metric: DistanceMetric = DistanceMetric.EUCLIDEAN
        ) -> None:
        """
        Initialize this RecommendationsManager. Provide the pd.DataFrame, the list of features to use for the classification,
        the type of classifier (unitialized class), and the distance metric to use with the classifier. 
        An initialized SpotifyManager must be passed to resolve the recommendations' album arts and spotify urls.
        """
        self.data = data
        self.features = features
        self.spotify_manager = spotify_manager
        self.classifier = classifier # classifier should be uninitialized here.
        self.dist_metric = dist_metric
        
    def _normalize_data(self, numerical_only_data: pd.DataFrame) -> np.ndarray:
        """
        Returns a numpy array where each feature of the df is scaled between 0 and 1.
        The input dataframe must only contain numerical features.
        """
        scaler = MinMaxScaler()
        normalized_data = scaler.fit_transform(numerical_only_data)
        return normalized_data
    
    def _convert_df_to_songs(self, recommended_songs: pd.DataFrame, query_name: str) -> list[Song]:
        """
        Provided a dataframe of recommended_songs, create Song objects corresponding to each row
        in the df. Avoid duplicate songs, and skip the query record itself. 
        Each row of recommended_songs must have all the columns necessary to create a Song object.
        """
        seen_songs = set([query_name.lower()])
        print(f'{query_name = }')
        songs: list[Song] = []
        for index in range(len(recommended_songs)):
            song_name: str = recommended_songs['name'].iloc[index]
            artist_name: str = ast.literal_eval(recommended_songs['artists'].iloc[index])[0]

            # avoid duplicate Songs
            if (lowercase_song_name := song_name.lower()) in seen_songs:
                continue
            seen_songs.add(lowercase_song_name)
            
            if (song := self.spotify_manager.search_song(song_name, artist_name)) is not None:
                songs.append(song)
        return songs
    
    def _get_classifier_results(self, data_copy: pd.DataFrame, normalized_data: pd.DataFrame, query: np.ndarray, k: int) -> list[Song]:
        """
        Given a song's acoustic features, run it thorugh our classifier, and get the k recommendations.
        """
        clf = self.classifier(k, self.dist_metric)
        clf.fit(normalized_data)
        distances, indices = clf.predict(query)
        recommended_songs = data_copy.iloc[indices]

        # debugging console output
        query_name: str = data_copy.iloc[-1]['name']
        query_artist: str = ast.literal_eval(data_copy.iloc[-1]['artists'])[0]
        print(f'\nKNN Recommended Songs for {query_name} by {query_artist}:')
        for index in range(len(recommended_songs)):
            song_name = recommended_songs['name'].iloc[index]
            artist = ast.literal_eval(recommended_songs['artists'].iloc[index])[0]
            print(f'{index + 1}. {song_name} by {artist}')
        return self._convert_df_to_songs(recommended_songs, query_name)
    
    def get_recommendations(self, query: Song, num_recommendations: int = 5) -> list[Song]:
        """
        Given a query, run it through self.classifier and get a list of Song recommendations.
        """
        # add this query to a copy of the dataset, normalize the data with the query in it, then call the classifier.
        # the copying needs to be done otherwise normalization of the query will be incorrect.
        data_copy = self.data.copy()
        data_copy.loc[len(data_copy.index)] = query.get_features_to_create_df_entry()
        normalized_data = self._normalize_data(data_copy[self.features])
        normalized_query_record: np.ndarray = normalized_data[-1]

        # TODO: add gpu_knn functionality and split up this conditional as needed
        if self.classifier in [MyKNeighborsClassifier, GpuKNeighbors]:
            songs = self._get_classifier_results(
                data_copy=data_copy,
                normalized_data=normalized_data,
                query=normalized_query_record,
                k=num_recommendations
            )
            logger.info(
                f'get_recommendations(classifier=knn, query={query.song_name}), returning {json.dumps([s.to_dict() for s in songs], indent=4)}'
            )
            return songs
        else:
            raise ValueError(f'Invalid classifier {self.classifier}!')

# test code, see if it works
if __name__ == '__main__':
    data = pd.read_csv('./data/data.csv')
    spotify_manager = SpotifyManager()
    recommendations_manager = RecommendationsManager(data, DATA_FEATURES, spotify_manager)
    
    # 2 different songs to try out here
    # song = spotify_manager.search_song(song_name='Pedal Point Blues', artist_name='Charles Mingus')
    song = spotify_manager.search_song(song_name='Forever Young', artist_name='BLACKPINK')
    print(f'In rec Manager, got this song: {song}')
    recommendations = recommendations_manager.get_recommendations(query=song, num_recommendations=10)
    print(json.dumps([f'{s.song_name} by {s.artist_name}' for s in recommendations], indent=4))
        