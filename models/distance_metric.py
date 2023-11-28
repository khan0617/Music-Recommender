from enum import Enum, auto

class DistanceMetric(Enum):
    """
    Represents all available distance metrics for the SongClassifiers.
    """
    EUCLIDEAN = auto()
    MANHATTAN = auto()