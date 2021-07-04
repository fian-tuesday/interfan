import numpy as np
import rpc


lower_threshold = 20  # порог, ниже которого всё считаем чёрной полосой
upper_threshold = 200  # порог, выше которого всё считаем белой полосой


@rpc.remote
def get_all_base_points(brightness_array: np.ndarray):
    height, width = brightness_array.shape
    all_black_base_points = set()
    all_white_base_points = set()
    for x in range(width):
        data_slice = brightness_array[:, x]
        black_base_points = [y for y in range(height) if data_slice[y] < lower_threshold]
        white_base_points = [y for y in range(height) if data_slice[y] > upper_threshold]

        all_black_base_points.update((x, y) for y in black_base_points)
        all_white_base_points.update((x, y) for y in white_base_points)

    return set(all_black_base_points), set(all_white_base_points)

