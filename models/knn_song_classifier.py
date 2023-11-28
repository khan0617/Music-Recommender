import numpy as np
from abc import ABC, abstractmethod
from .distance_metric import DistanceMetric

class KnnSongClassifier(ABC):
    """
    Abstract class for any knn-based song classifier.
    """
    @abstractmethod
    def __init__(self, k: int, dist_metric: DistanceMetric) -> None:
        raise NotImplementedError

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray | None) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def predict(self, query: np.ndarray) -> tuple[list[np.ndarray], list[np.ndarray]]:
        raise NotImplementedError