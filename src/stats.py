from collections import deque
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


class StatsController:
    def __init__(self):
        self.stats_data = {label: [] for label in stats_labels}
        # self.smoothing_data = {
        #     label: deque(maxlen=WINDOW_SIZE) for label in stats_labels
        # }
        self.stats_time = []

    def process_frame(self, grid: np.ndarray[float]):
        self.mean_intensity = np.mean(grid)
        self.std_dev = np.std(grid)
        self.median_intensity = np.median(grid)
        self.weighted_x, self.weighted_y = center_of_mass(grid)
        self.min_temp = np.min(grid)
        self.max_temp = np.max(grid)

        self.stats_data["Mean Intensity"].append(self.mean_intensity)
        self.stats_data["Standard Deviation"].append(self.std_dev)
        self.stats_data["Median"].append(self.median_intensity)
        self.stats_data["Weighted X"].append(self.weighted_x)
        self.stats_data["Weighted Y"].append(self.weighted_y)
        self.stats_data["Min"].append(self.min_temp)
        self.stats_data["Max"].append(self.max_temp)

        # for label in stats_labels:
        #     self.smoothing_data[label].append(self.stats_data[label][-1])

        self.stats_time.append(time.time())

        if len(self.stats_time) > MAX_VALUES:
            self.stats_time.pop(0)
            for label in stats_labels:
                self.stats_data[label].pop(0)


def center_of_mass(grid):
    max_pos = np.unravel_index(np.argmax(grid), grid.shape)
    return max_pos
