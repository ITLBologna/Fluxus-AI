import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from time import sleep

import cv2
import numpy as np
from dearpygui import dearpygui as dpg
from path import Path

from conf import cnf
from front_end import dpg_img
from front_end import dpg_hist
from front_end import loading_modal, error_modal
from front_end.dir_analyzer import DirAnalyzer
from threading import Thread


def check_ts(ts):
    ts = ts.split(':')
    if len(ts) != 3:
        return False

    for component in ts:
        if len(component) != 2:
            return False

    return True


def _read_csv(csv_path):
    csv_array = []
    with open(csv_path) as f:
        f.readline()
        for l in f:
            row = l.strip().split(', ')
            csv_array.append(np.array(row))
    return np.asarray(csv_array)

def reset_popup(tag, sec):
    sleep(sec)
    dpg.set_value(tag, '')


class SideBar(object):

    def reset_conf_and_data(self):
        # type: () -> None
        """
        >> Callback for "RESET" button;
        >> reset and delete current conf and data
        """

        if self.in_dir_path is None:
            dpg.set_value('reset_popup', 'Nothing to remove')
            Thread(target=reset_popup, args=("reset_popup", 4)).run()

        else:
            answer = messagebox.askyesno("Delete Config and CSV files",
                                         "This operation will delete config and csv files. Continue?")
            if answer:
                for d in ["calib.json", "data.csv", "full_video.dat", "full_video.trk"]:
                    if (self.in_dir_path / d).exists():
                        (self.in_dir_path / d).remove()

                dpg_hist.update_dpg_hist(bar_heights=[0 for i in range(12)])
                self.reset_data_struct()


    def filter_cb(self, sender, *_args, **_kwargs):
        value = dpg.get_value(sender)

        k1, k2 = sender.split('@')
        self.dict[k1][k2] = value
        if k1 == 'timestamp' and not check_ts(value):
            return

        print(f'$> set filter option in section `{k1}`: `{k2}={value}`')


    def file_cb(self, *_args, **_kwargs):
        root = tk.Tk()
        root.withdraw()
        selected_path = filedialog.askdirectory()
        self.in_dir_path = Path(selected_path).abspath()
        dpg.set_value('in_dir', f'({self.in_dir_path.basename()})')

        if len(self.in_dir_path.files("*.MP4")) <= 0:
            messagebox.showerror("Error", "No '.MP4' file found")
            self.reset_data_struct()
        else:
            loading_modal.show_modal(True)
            DirAnalyzer(
                in_dir=self.in_dir_path,
                done_callback=self.load_complete
            ).start()

            # self.csv_array = _read_csv(self.in_dir_path)
            print(f'$> selected new input directory: "{self.in_dir_path}"')


    def load_complete(self, status):
        print('DONE')

        loading_modal.show_modal(False)
        loading_modal.reset_modal()
        if status is True or isinstance(status, list) or isinstance(status, np.ndarray):
            self.csv_array = _read_csv(self.in_dir_path / 'data.csv')
        else:
            self.reset_data_struct()

    def __init__(self, width, height):

        with dpg.child_window(width=width, height=height):
            self.w = width
            self.h = height

            self.init_logo()
            self.add_sec_separator()

            self.init_file_sec()
            self.add_sec_separator()

            self.init_conf_reset_sec()
            self.add_sec_separator()

            self.init_vclass_sec()
            self.add_sec_separator()

            # self.init_lane_sec()
            # self.add_sec_separator()

            self.init_timestamp_sec()
            loading_modal.build_modal()

            self.reset_data_struct()

    def reset_data_struct(self):
        self.in_dir_path = None
        self.csv_array = None

        self.dict = {}
        self.init_dict()

        dpg.set_value('in_dir', '(no input directory selected)')

        loading_modal.reset_modal()
        loading_modal.show_modal(False)

    def init_logo(self):
        root = Path(__file__).parent.parent
        img = cv2.imread(root / 'resources' / 'app_logo.png')[:, :, ::-1]
        img = cv2.resize(
            img, (0, 0), fx=0.9, fy=0.9,
            interpolation=cv2.INTER_AREA
        )
        h, w = img.shape[:2]
        dpg_img.init_texture('img_tex', img, aspect_ratio=w / h, desired_w=w)
        dpg.add_image('img_tex')
        dpg.add_spacer(height=4)


    def init_dict(self):

        self.dict['vclass'] = {}
        for vclass in cnf.v_classes:
            self.dict['vclass'][vclass] = True

        # self.dict['lane'] = {}
        # for lane in cnf.lanes:
        #     self.dict['lane'][lane] = True

        self.dict['timestamp'] = {}
        self.dict['timestamp']['start'] = None
        self.dict['timestamp']['end'] = None


    def add_sec_separator(self):
        dpg.add_spacer(height=4)
        dpg.add_separator()
        dpg.add_spacer(height=4)


    def init_file_sec(self):
        dpg.add_text('Select an input directory')
        dpg.add_text(
            'select the directory containing the video files to process',
            wrap=self.w - 50, color=(211, 217, 231, 128)
        )
        dpg.add_spacer(height=2)
        with dpg.group(horizontal=True):
            dpg.add_button(
                label='select', tag='select_btn',
                callback=self.file_cb, width=80
            )
            dpg.add_text('(no input directory selected)', tag='in_dir')

    def init_conf_reset_sec(self):
        dpg.add_text('Delete config and csv files')
        dpg.add_spacer(height=2)
        with dpg.group(horizontal=True):
            dpg.add_button(
                label='Reset', tag='reset_btn',
                callback=self.reset_conf_and_data, width=80,
            )
            dpg.add_text('', tag='reset_popup')




    def init_vclass_sec(self):
        dpg.add_text('Select vehicle type')
        dpg.add_text(
            'you can select one or more vehicle types',
            wrap=self.w - 50, color=(211, 217, 231, 128)
        )
        dpg.add_spacer(height=2)

        with dpg.table(header_row=False):
            dpg.add_table_column()
            dpg.add_table_column()
            dpg.add_table_column()
            for i in range(3):
                with dpg.table_row():
                    for j in range(3):
                        if i * 3 + j >= len(cnf.v_classes):
                            continue
                        v_class = cnf.v_classes[i * 3 + j]
                        # v_class = v_class.replace('veicolo commerciale', 'v.c.')
                        dpg.add_checkbox(
                            label=v_class, default_value=True,
                            callback=self.filter_cb, tag='vclass@' + v_class
                        )


    # def init_lane_sec(self):
    #     dpg.add_text('Seleziona corsia')
    #     dpg.add_text(
    #         'puoi selezionare una o più corsie',
    #         wrap=self.w - 50, color=(211, 217, 231, 128)
    #     )
    #     dpg.add_spacer(height=2)
    #     with dpg.table(header_row=False):
    #         dpg.add_table_column()
    #         dpg.add_table_column()
    #         dpg.add_table_column()
    #         with dpg.table_row():
    #             dpg.add_checkbox(
    #                 label='corsia1', default_value=True,
    #                 callback=self.filter_cb, tag='lane@corsia1'
    #             )
    #             dpg.add_checkbox(
    #                 label='corsia2', default_value=True,
    #                 callback=self.filter_cb, tag='lane@corsia2'
    #             )


    def init_timestamp_sec(self):
        dpg.add_text('Select time interval')
        dpg.add_text(
            'select a time interval or leave all field black '
            'to select the entire video',
            wrap=self.w - 50, color=(211, 217, 231, 128)
        )
        dpg.add_spacer(height=3)
        with dpg.group(horizontal=True):
            dpg.add_input_text(
                label='start', width=84, hint='hh:mm:ss',
                callback=self.filter_cb, tag='timestamp@start'
            )
            dpg.add_spacer(width=5)
            dpg.add_input_text(
                label='end', width=84, hint='hh:mm:ss',
                callback=self.filter_cb, tag='timestamp@end'
            )
