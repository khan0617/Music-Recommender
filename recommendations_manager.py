import ast
import logging
import pandas as pd
import json
from sklearn.preprocessing import MinMaxScaler
from spotify_manager import SpotifyManager
from my_k_neighbors_classifier import MyKNeighborsClassifier
from logging_config import setup_logging
from song import Song

DATA_FEATURES = ['valence', 'acousticness', 'danceability', 'energy', 
                 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo']

setup_logging()
logger = logging.getLogger(__name__)

class RecommendationsManager:
    """Class to handle getting song recommendations given an input song."""
    def __init__(self, data: pd.DataFrame, features: list[str], spotify_manager: SpotifyManager, classifier: str = 'knn', dist_metric: str = 'euclidean') -> None:
        """
        Initialize this RecommendationsManager. Provide the pd.DataFrame, the list of features to use for the classification,
        the type of classifier, and the distance metric to use with the classifier. SpotifyManager must be passed in
        to resolve the recommendations' album arts and spotify urls.
        """
        self.data = data
        self._normalized_data = self._normalize_data(data[features])
        self.features = features
        self.spotify_manager = spotify_manager
        self.classifier = classifier
        self.dist_metric = dist_metric
        
    @staticmethod
    def _normalize_data(numerical_only_data: pd.DataFrame) -> pd.DataFrame:
        """
        Returns a DataFrame where each feature is scaled between 0 and 1.
        The input dataframe must only contain numerical features.
        """
        scaler = MinMaxScaler()
        normalized_data = scaler.fit_transform(numerical_only_data)
        return normalized_data
    
    def _convert_df_to_songs(self, recommended_songs: pd.DataFrame) -> list[Song]:
        """
        Provided a dataframe of recommended_songs, create Song objects corresponding to each row
        in the df. Each row must have all the columns necessary to create a song.
        """
        songs: list[Song] = []
        for index in range(len(recommended_songs)):
            song_name = recommended_songs['name'].iloc[index]
            artist_name = ast.literal_eval(recommended_songs['artists'].iloc[index])[0]
            if (song := self.spotify_manager.search_song(song_name, artist_name)) is not None:
                songs.append(song)
        return songs
    
    def _get_knn_results(self, query_features: list[float], k: int) -> list[Song]:
        """
        Given a song's acoustic features, run it thorugh knn and get the k recommendations.
        """
        knn = MyKNeighborsClassifier(k, self.dist_metric)
        knn.fit(self._normalized_data)
        distances, indices = knn.predict(query=query_features)
        recommended_songs = self.data.iloc[indices]
        print('\nKNN Recommended Songs:')
        for index in range(len(recommended_songs)):
            song_name = recommended_songs['name'].iloc[index]
            artist = ast.literal_eval(recommended_songs['artists'].iloc[index])[0]
            print(f'{index + 1}. {song_name} by {artist}')
        return self._convert_df_to_songs(recommended_songs)
    
    def get_recommendations(self, query: Song, num_recommendations: int = 5) -> list[Song]:
        """
        Given a query, run it through self.classifier and get a list of Song recommendations.
        """
        query_features = query.get_features(feature_names=self.features)
        if self.classifier == 'knn':
            songs = self._get_knn_results(query_features=query_features, k=num_recommendations)
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
    song = spotify_manager.search_song(song_name='Pedal Point Blues', artist_name='Charles Mingus')
    print(f'In rec Manager, got this song: {song}')
    recommendations = recommendations_manager.get_recommendations(query=song)
    print(json.dumps([s.to_dict() for s in recommendations], indent=4))
        