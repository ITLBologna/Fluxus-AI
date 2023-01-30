import dearpygui.dearpygui as dpg
import numpy as np

from front_end import dpg_hist
from front_end import error_modal
from front_end import theme
from front_end.side_bar import SideBar
from queryzator.quryzator import build_histogram


WIN_H = 720
WIN_W = 1100

WIN_PAD = 20
WL = 400
H_SKIP = 8
W_SKIP = 16
WR = WIN_W - WL - W_SKIP - 2 * WIN_PAD
PLOT_H = 459
HEADER_H = 70


class App(object):

    @staticmethod
    def init_dpg():
        dpg.create_context()
        dpg.create_viewport()
        dpg.setup_dearpygui()


    @staticmethod
    def init_header():
        # type: () -> None
        """
        Init APP header; it's the top row of the APP and it
        contains the logo.
        """
        width = WIN_W - 2 * WIN_PAD
        with dpg.child_window(width=width, height=HEADER_H):
            pass


    def init_plot_area(self):
        with dpg.group():
            with dpg.child_window(width=WR, height=PLOT_H):
                dpg.add_text('Total: -- vehicles', tag='tot')
                dpg_hist.init_histogram(height=PLOT_H - 70, width=-1)

            dpg.add_spacer(height=H_SKIP)
            with dpg.child_window(width=WR, height=125):
                dpg.add_spacer(height=5)
                dpg.add_text(
                    'Process data and export elaboration '
                    'into CSV format'
                    'or reset to initial configuration'
                )
                dpg.add_spacer(height=3)
                with dpg.group(horizontal=True, horizontal_spacing=W_SKIP):
                    dpg.add_button(
                        label='Show query', width=128, height=32,
                        callback=self.analyze_cb
                    )


    def analyze_cb(self):
        # type: () -> None
        """
        >> Callback for "ANALYZE" button;
        >> Updates histogram w.r.t. the current query.
        """
        if self.side_bar.csv_array is None:
            error_modal.set_header(
                'No input directory found. Select an input '
                'directory before start the elaboration'
            )
            error_modal.show_modal(True)
        else:
            ys = build_histogram(
                self.side_bar.dict,
                self.side_bar.csv_array,
                bin_width=15,
            )
            dpg_hist.update_dpg_hist(bar_heights=ys)
            dpg.set_value('tot', f'Total: {np.sum(ys)} vehicles')



    def __init__(self, name='FluxusAI'):
        # type: (str) -> None
        self.name = name
        self.init_dpg()

        with dpg.window(tag=self.name, width=WIN_W, height=WIN_H):
            # self.init_header()
            # dpg.add_spacer(height=H_SKIP)

            with dpg.group(horizontal=True, horizontal_spacing=W_SKIP):
                self.side_bar = SideBar(width=WL, height=680)
                self.init_plot_area()

            error_modal.build_modal()

        t, f = theme.get_theme_and_font()
        dpg.bind_item_theme(self.name, t)
        dpg.bind_font(f)


    def run(self):
        dpg.set_primary_window(self.name, True)
        dpg.set_viewport_width(WIN_W)
        dpg.set_viewport_height(WIN_H)
        dpg.set_viewport_title(self.name)
        dpg.show_viewport()
        dpg.start_dearpygui()
