import ast
import logging
import json
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
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
        songs: list[Song] = []
        order_map = {}  # we'll need to maintain order after resolving the futures

        # helper function that the parallel workers will execute
        def get_song_object(index: int, song_name: str, artist_name: str):
            if song_name.lower() in seen_songs:
                return None, None
            seen_songs.add(song_name.lower())
            song = self.spotify_manager.search_song(song_name, artist_name)
            return index, song

        # parallelize the API calls
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(get_song_object, i, recommended_songs['name'].iloc[i], 
                                       ast.literal_eval(recommended_songs['artists'].iloc[i])[0]) 
                       for i in range(len(recommended_songs))]

            for future in as_completed(futures):
                index, song = future.result()
                if song is not None:
                    order_map[index] = song

        # build the ordered list of songs
        for index in sorted(order_map.keys()):
            songs.append(order_map[index])

        return songs
    
    def _get_knn_results(self, data_copy: pd.DataFrame, normalized_data: pd.DataFrame, query: np.ndarray, k: int) -> list[Song]:
        """
        Given a song's acoustic features, run it thorugh our CPU knn classifier, and get the k recommendations.
        """
        clf = MyKNeighborsClassifier(k, self.dist_metric, jit_compilation=False)
        clf.fit(normalized_data)
        distances, indices = clf.predict(query)
        recommended_songs = data_copy.iloc[indices]
        query_name: str = data_copy.iloc[-1]['name']

        self._print_classifier_results(data_copy, recommended_songs)
        return self._convert_df_to_songs(recommended_songs, query_name)
    
    def _get_gpu_knn_results(self, data_copy: pd.DataFrame, normalized_data: pd.DataFrame, query: np.ndarray, k: int) -> list[Song]:
        """
        Given a song's acoustic features, run it thorugh our GPU knn classifier, and get the k recommendations.
        """
        clf = GpuKNeighbors(k, self.dist_metric)
        clf.fit(normalized_data)
        distances, indices = clf.predict(query)
        recommended_songs = data_copy.iloc[indices]
        query_name: str = data_copy.iloc[-1]['name']

        self._print_classifier_results(data_copy, recommended_songs)
        return self._convert_df_to_songs(recommended_songs, query_name)
    
    def _print_classifier_results(self, data_copy: pd.DataFrame, recommended_songs: pd.DataFrame) -> None:
        """
        Print the classifier results for debugging purposes.
        """
        query_name: str = data_copy.iloc[-1]['name']
        query_artist: str = ast.literal_eval(data_copy.iloc[-1]['artists'])[0]
        print(f'\n{self.classifier.__name__} Recommended Songs for {query_name} by {query_artist}:')
        for index in range(len(recommended_songs)):
            song_name = recommended_songs['name'].iloc[index]
            artist = ast.literal_eval(recommended_songs['artists'].iloc[index])[0]
            print(f'{index + 1}. {song_name} by {artist}')
    
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

        songs: list[Song] = None
        if self.classifier == MyKNeighborsClassifier:
            songs = self._get_knn_results(
                data_copy=data_copy,
                normalized_data=normalized_data,
                query=normalized_query_record,
                k=num_recommendations
            )
        elif self.classifier == GpuKNeighbors:
            songs = self._get_gpu_knn_results(
                data_copy=data_copy,
                normalized_data=normalized_data,
                query=normalized_query_record,
                k=num_recommendations,
            )
        else:
            raise ValueError(f'Invalid classifier {self.classifier}!')
        
        logger.info(
            f'get_recommendations(classifier={self.classifier.__name__}, query={query.song_name}), returning {json.dumps([s.to_dict() for s in songs], indent=4)}'
        )

        return songs


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
        