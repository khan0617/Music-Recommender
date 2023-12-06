import math
import numpy as np
from .distance_metric import DistanceMetric
from numba import cuda, void, float64, int32

THREADS_PER_BLOCK = 256

# query point will be stored in constant memory due to constant reuse across threads.
# numba requires that constant memory is allocated in a cuda.jit() function.
QUERY: cuda.devicearray.DeviceNDArray = None

@cuda.jit(device=True)
def _gpu_euclidean(
    query: cuda.devicearray.DeviceNDArray, 
    point: cuda.devicearray.DeviceNDArray, 
    num_features: int
) -> float:
    """
    GPU device function to calculate euclidean distance between query and point arrays.
    """
    sum = 0.0
    for i in range(num_features):
        diff = query[i] - point[i]
        sum += diff * diff
    return math.sqrt(sum)

@cuda.jit(device=True)
def _gpu_manhattan(
    query: cuda.devicearray.DeviceNDArray, 
    point: cuda.devicearray.DeviceNDArray, 
    num_features: int
) -> float:
    """
    GPU device function to calculate Manhattan distance between query and point arrays.
    """
    sum = 0.0
    for i in range(num_features):
        sum += math.fabs(query[i] - point[i])
    return sum

@cuda.jit
def distance_kernel(
    data: cuda.devicearray.DeviceNDArray, 
    distances: cuda.devicearray.DeviceNDArray, 
    num_songs: int, 
    num_features: int, 
    dist_metric: int
) -> None:
    """
    Kernel to calculate distances from the query to each point in the dataset.
    - data: dataset
    - distances: output array for distances
    - num_songs: number of songs in the dataset
    - num_features: number of features per song
    - dist_metric: distance metric (0 for Euclidean, 1 for Manhattan)
    """
    query_c = cuda.const.array_like(QUERY) # query is stored in cached constant memory
    idx = cuda.grid(1)
    if idx < num_songs:
        point = data[idx * num_features : (idx + 1) * num_features]
        if dist_metric == 0:
            distances[idx] = _gpu_euclidean(query_c, point, num_features)
        elif dist_metric == 1:
            distances[idx] = _gpu_manhattan(query_c, point, num_features)

class GpuKNeighbors:
    def __init__(self, k: int, dist_metric: DistanceMetric = DistanceMetric.EUCLIDEAN) -> None:
        self.X = None
        self.y = None
        self.k = k
        self.dist_metric = dist_metric

    def fit(self, X: np.ndarray, y: np.ndarray | None = None) -> None:
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
        global QUERY
        QUERY = query.ravel()
        num_songs = self.X.shape[0]
        num_features = self.X.shape[1]
        dist_metric = 0 if self.dist_metric is DistanceMetric.EUCLIDEAN else 1

        # Flatten the dataset to a 1D array for GPU processing
        self.X = self.X.ravel()

        # move data to the GPU
        d_data = cuda.to_device(self.X)
        d_distances = cuda.device_array(num_songs, dtype=np.float32)

        # launch the kernel then synchronize
        num_blocks = (num_songs + THREADS_PER_BLOCK - 1) // THREADS_PER_BLOCK
        distance_kernel[num_blocks, THREADS_PER_BLOCK](d_data, d_distances, num_songs, num_features, dist_metric)
        cuda.synchronize()
        
        # move the results back to the host
        h_distances = d_distances.copy_to_host()

        print(f'\nGpuKNN(dist_metric={self.dist_metric}), first k={self.k} unsorted distances:')
        for i in range(min(self.k, len(h_distances))):
            print(f'Distance {i}: {h_distances[i]}')

        # use np.argsort to find the indices of the k nearest neighbors
        indices = np.argsort(h_distances)[:self.k]

        return h_distances[indices], indices