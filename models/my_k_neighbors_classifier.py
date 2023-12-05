import numpy as np
from typing import Any
from numba import jit, float64
from .distance_metric import DistanceMetric
from .knn_song_classifier import KnnSongClassifier

@jit(float64(float64[:], float64[:]), nopython=True)
def _jit_euclidean(query: np.ndarray, point: np.ndarray) -> float:
    """
    Just in time compiled version of euclidean distance calculation.
    """
    return np.sqrt(np.sum((query - point) ** 2))

@jit(float64(float64[:], float64[:]), nopython=True)
def _jit_manhattan(query: np.ndarray, point: np.ndarray) -> float:
    """
    Just in time compiled version of manhattan distance calculation.
    """
    return np.sum(np.abs(query - point))

class MyKNeighborsClassifier(KnnSongClassifier):
    def __init__(
        self, 
        k: int, 
        dist_metric: DistanceMetric = DistanceMetric.EUCLIDEAN, 
        jit_compilation: bool = True
    ) -> None:
        self.k = k
        self.dist_metric = dist_metric
        self.X = None
        self.y = None
        self.jit_compilation = jit_compilation

    @staticmethod
    def _euclidean(query: np.ndarray, point: np.ndarray) -> float:
        """
        Calculate euclidean distance between two points in N-d space.

        Params:
            - query (np.ndarray): the query point (the one the user passed in)
            - point (np.ndarray): a song from the dataset to compare against query

        Returns:
            - float: Euclidean distance between query and point.
        """
        return np.sqrt(np.sum((query - point) ** 2))
    
    @staticmethod
    def _manhattan(query: np.ndarray, point: np.ndarray) -> float:
        """
        Calculate manhattan distance between two points in N-d space.

        Params:
            - query (np.ndarray): the query point (the one the user passed in)
            - point (np.ndarray): a song from the dataset to compare against query

        Returns:
            - float: Manhattan distance between query and point.
        """
        return np.sum(np.abs(query - point))

    def fit(self, X: np.ndarray, y: Any = None) -> None:
        """
        Fit this KNN classifier with the data.
        """
        self.X = X
        self.y = y

    def predict(self, query: np.ndarray) -> tuple[list[np.ndarray], list[np.ndarray]]:
        """
        Find the k nearest neighbors. Compare a single query point to every point in the dataset.

        Params:
            - query (np.ndarray): the point we want the k neighbors for (the song the user input).

        Returns:
            - tuple(distances, indices) for the k neighbors for each point.
        """
        if self.dist_metric is DistanceMetric.EUCLIDEAN:
            distance_func = _jit_euclidean if self.jit_compilation else self._euclidean
        elif self.dist_metric is DistanceMetric.MANHATTAN:
            distance_func = _jit_manhattan if self.jit_compilation else self._manhattan
        else:
            raise ValueError(f'Unsupported distance metric: {self.dist_metric}')

        distances = np.array([distance_func(query, point) for point in self.X])

        # find indices of k smallest distances
        indices = np.argsort(distances)[:self.k]
        return distances[indices], indices
    