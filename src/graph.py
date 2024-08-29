from collections import deque
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import stats


class GraphController:
    def __init__(self):
        # Create a figure and axis
        plt.ion()
        stats_ax: plt.Axes
        grid_ax: plt.Axes
        fig, (grid_ax, stats_ax) = plt.subplots(1, 2)
        fig.canvas.mpl_connect(
            "close_event", lambda x: exit(0)
        )  # listen to close event

        # Initialize variables
        weighted_x_history = deque(maxlen=stats.WINDOW_SIZE)
        last_midi_value = 0
        smoothed_value = 0

        # Plot the grid using a colormap
        self.im = grid_ax.imshow(
            [[0]],
            cmap="hot",
            vmin=stats.MIN_TEMP,
            vmax=stats.MAX_TEMP,
            interpolation="bicubic",
        )
        im2 = grid_ax.imshow([[0]], interpolation="nearest")

        # Add a colorbar
        cbar = grid_ax.figure.colorbar(self.im, ax=grid_ax)

        self.stats_lines: list[Line2D] = []
        for i in range(len(stats.stats_labels)):
            (line,) = stats_ax.plot([], [], label=stats.stats_labels[i])
            self.stats_lines.append(line)

        stats_ax.set_title("Stats")
        stats_ax.set_xlabel("Time")
        stats_ax.set_ylabel("Normalized Value")
        stats_ax.legend()

    def process_frame(self, grid: np.NDArray[float], stats_ctlr: stats.StatsController):

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

        stats_ax.relim()
        stats_ax.autoscale_view()

        # Show the plot
        fig.canvas.draw()
        plt.draw()
        fig.canvas.flush_events()
