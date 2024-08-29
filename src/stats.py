import time
import numpy as np


stats_labels = [
    "Mean Intensity",
    "Standard Deviation",
    "Median",
    "Weighted X",
    "Weighted Y",
    "Min",
    "Max",
]

MIN_TEMP = 0
MAX_TEMP = 37.5
TRIGGER_TEMP = 15
TRIGGER_FROM_MEAN = 3
TRIGGER_FROM_MIN = 3
MAX_VALUES = 50

# New Constants
WINDOW_SIZE = 10  # Number of samples to consider for moving average
HYSTERESIS = 0.05  # Minimum change required to update MIDI value
SMOOTHING_FACTOR = 0.2  # Exponential smoothing factor (0 to 1)


class StatsController:
    def __init__(self):
        self.stats_data = {label: [] for label in stats_labels}
        self.stats_time = []

    def process_frame(self, grid: np.NDArray[float]):
        self.mean_intensity = np.mean(grid)
        self.std_dev = np.std(grid)
        self.median_intensity = np.median(grid)
        self.weighted_x, self.weighted_y = weighted_center_of_mass(grid)
        self.min_temp = np.min(grid)
        self.max_temp = np.max(grid)

        self.stats_data["Mean Intensity"].append(self.mean_intensity)
        self.stats_data["Standard Deviation"].append(self.std_dev)
        self.stats_data["Median"].append(self.median_intensity)
        self.stats_data["Weighted X"].append(self.weighted_x)
        self.stats_data["Weighted Y"].append(self.weighted_y)
        self.stats_data["Min"].append(self.min_temp)
        self.stats_data["Max"].append(self.max_temp)

        self.stats_time.append(time.time())

        if len(self.stats_time) > MAX_VALUES:
            self.stats_time.pop(0)
            for label in stats_labels:
                self.stats_data[label].pop(0)


def weighted_center_of_mass(grid):
    """Calculates the weighted center of mass of a grid.

    Args:
      grid: A 2D numpy array representing the grid of values.

    Returns:
      A tuple representing the x and y coordinates of the center of mass.
    """

    # Ensure grid is a numpy array
    grid = np.array(grid)

    # Calculate total weight
    total_weight = np.sum(grid)

    # Calculate weighted coordinates
    x_weighted_sum = np.sum(np.multiply(grid, np.arange(grid.shape[1])))
    y_weighted_sum = np.sum(np.multiply(grid, np.arange(grid.shape[0])[:, np.newaxis]))

    # Calculate center of mass
    x_center = x_weighted_sum / total_weight
    y_center = y_weighted_sum / total_weight

    return x_center, y_center
