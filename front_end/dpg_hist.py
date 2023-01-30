import numpy as np
from dearpygui import dearpygui as dpg


def init_histogram(height, width):
    # type: (int, int) -> None
    """
    Build an empy histogram inside a container with
    the input height and width.

    :param height: height of the histogram container
    :param width: width of the histogram container
    """

    with dpg.plot(label=' ', height=height, width=width,
                  no_mouse_pos=True, no_menus=True):
        # build an empty histogram with 12 bins
        # >> height of each bin: 0
        ys = np.zeros((12,))
        xs = np.arange(0, len(ys))
        labels = tuple((f'T{i}', i) for i in range(len(ys)))

        x_ax_label = 'time (15 min interval)'
        dpg.add_plot_axis(
            dpg.mvXAxis, label=x_ax_label,
            no_gridlines=True, tag='x_ax'
        )
        dpg.set_axis_limits(dpg.last_item(), -1, len(ys))
        dpg.set_axis_ticks(dpg.last_item(), labels)

        with dpg.plot_axis(dpg.mvYAxis, label='count', tag='y_ax'):
            y_max = np.max(ys)
            y_max = int(round(y_max + 0.1 * y_max))
            if y_max == 0:
                dpg.set_axis_limits(dpg.last_item(), 0, 42)
            dpg.add_bar_series(list(xs), list(ys), weight=0.8, tag='hist')


def update_dpg_hist(bar_heights):
    # type: (np.ndarray) -> None
    """
    :param bar_heights: array with shape: (N,) where N
        is the number of histogram bars; the i-th element
        of this array is an int that represents the height
        of the i-th bar of the histogram
    """
    bar_heights = bar_heights
    n_bins = len(bar_heights)

    # change x-axis
    x_ticks = list(np.arange(0, n_bins))
    x_tick_labels = tuple((f'T{i}', i) for i in range(n_bins))
    dpg.set_axis_limits('x_ax', -1, n_bins)
    dpg.set_axis_ticks('x_ax', x_tick_labels)
    dpg.configure_item('hist', x=x_ticks)

    # change y-axis
    y_max = np.max(bar_heights)
    y_max = int(round(y_max + 0.1 * y_max))
    dpg.set_axis_limits('y_ax', 0, y_max)
    dpg.configure_item('hist', y=bar_heights)
