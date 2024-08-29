from collections import deque
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import src.stats as stats


class GraphController:
    stats_ax: plt.Axes
    grid_ax: plt.Axes

    def __init__(self):
        # Create a figure and axis
        plt.ion()
        self.fig, (self.grid_ax, self.stats_ax) = plt.subplots(1, 2)
        self.fig.canvas.mpl_connect(
            "close_event", lambda x: exit(0)
        )  # listen to close event

        # Initialize variables
        last_midi_value = 0
        smoothed_value = 0

        # Plot the grid using a colormap
        self.im = self.grid_ax.imshow(
            [[0]],
            cmap="hot",
            vmin=stats.MIN_TEMP,
            vmax=stats.MAX_TEMP,
            interpolation="bicubic",
        )
        im2 = self.grid_ax.imshow([[0]], interpolation="nearest")

        # Add a colorbar
        cbar = self.grid_ax.figure.colorbar(self.im, ax=self.grid_ax)

        self.stats_lines: list[Line2D] = []
        for i in range(len(stats.stats_labels)):
            (line,) = self.stats_ax.plot([], [], label=stats.stats_labels[i])
            self.stats_lines.append(line)

        self.stats_ax.set_title("Stats")
        self.stats_ax.set_xlabel("Time")
        self.stats_ax.set_ylabel("Normalized Value")
        self.stats_ax.legend()

    def process_frame(self, grid: np.ndarray[float], stats_ctlr: stats.StatsController):

        # data_above_range = grid > (min + TRIGGER_FROM_MIN)
        self.im.set_data(grid)

        data_above_range = grid > (stats.mean_intensity + stats.TRIGGER_FROM_MEAN)

        # VISUALISATION \/ \/

        # full blue if true, transparent if false
        data_above_range_color = np.zeros((*data_above_range.shape, 4))
        data_above_range_color[data_above_range] = [0, 0, 1, 0.5]

        self.im2.set_data(data_above_range_color)

        for i, line in enumerate(self.stats_lines):
            data = np.array(stats_ctlr.stats_data[stats.stats_labels[i]])
            # data = data / np.sqrt(np.sum(data**2))
            line.set_xdata(stats_ctlr.stats_time)
            line.set_ydata(data)

        self.stats_ax.relim()
        self.stats_ax.autoscale_view()

        # Show the plot
        self.fig.canvas.draw()
        plt.draw()
        self.fig.canvas.flush_events()
