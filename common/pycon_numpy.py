import numpy as np


def find_nearest_time(arr: np.ndarray, value: float):
    # arr = np.asarray(arr)
    idx = (np.abs(arr - value)).argmin()
    return (idx, arr[idx])
