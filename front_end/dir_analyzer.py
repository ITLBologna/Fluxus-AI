import json
from threading import Thread
from typing import Dict

import numpy as np
from path import Path

from back_end.video_analyzer import StreamAnalyzer
from front_end.line_selector import LineSelector
from front_end import loading_modal
from back_end.gopro_video_preprocessing import gopro_preprocess
from utils import write_csv

CALIB_JSON = 'calib.json'
DATA_CSV = 'data.csv'

class DirAnalyzer(Thread):
    def __init__(self, in_dir, done_callback=lambda _: None):
        super().__init__()
        self.in_dir = Path(in_dir)
        self.calib_dict = {}
        self.phase = 'initialization'
        self.done_callback = done_callback
        self.full_video_path = self.in_dir / "full_video.mp4"

    def run(self):

        if not needs_elaboration(self.in_dir):
            self.done_callback(True)
            return

        self.phase = f'Preprocessing {self.full_video_path} '
        loading_modal.set_header(self.phase)
        for progress in gopro_preprocess(self.in_dir, self.full_video_path):
            loading_modal.set_progress(progress)

        self.calib_dict = get_calib_dict(self.in_dir, self.full_video_path)
        if self.calib_dict is None:
            loading_modal.reset_modal()
            loading_modal.show_modal(False)
            self.done_callback(False)
            return

        self.phase = f'Processing {self.full_video_path} '

        analyzer = StreamAnalyzer(
            video_file=self.full_video_path,
            calib_dict=self.calib_dict
        )

        print(self.phase)
        loading_modal.set_header(self.phase)
        for progress in analyzer.run():
            print(f'\r\t->> running progress: {progress * 100:.2f} %', end='')
            loading_modal.set_progress(progress)

        csv_lines = analyzer.csv_info.tolist()
        csv_lines = sorted(np.asarray(csv_lines), key=lambda x: int(x[1]))

        write_csv(self.in_dir / "data.csv", csv_lines)

        self.done_callback(csv_lines)


def needs_calibration(dir_path):
    # type: (str) -> bool
    dir_path = Path(dir_path)
    calib_file = dir_path / CALIB_JSON
    return not calib_file.exists()


def needs_elaboration(dir_path):
    # type: (str) -> bool
    dir_path = Path(dir_path)
    data_file = dir_path / DATA_CSV
    return not data_file.exists()


def get_calib_dict(dir_path, video_path):
    # type: (str, str) -> Dict[str, Dict[str, ...]]
    dir_path = Path(dir_path)

    if needs_calibration(dir_path):
        print(f'$> there is no "{CALIB_JSON}" file in "{dir_path}"')

        print(f'$> please, select flow line for video "{video_path}"')
        key = video_path.basename()
        ls = LineSelector(video_path=video_path, win_name=key)
        calib_dict = ls.run()
        if calib_dict is not None:
            with open(dir_path / CALIB_JSON, 'w') as out_file:
                json.dump(calib_dict, out_file)
    else:
        with open(dir_path / CALIB_JSON, 'r') as in_file:
            calib_dict = json.load(in_file)

    return calib_dict


if __name__ == '__main__':
    DirAnalyzer(in_dir=Path('../resources/demo_video').abspath()).start()
