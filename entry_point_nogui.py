import click
import json
import numpy as np
from path import Path
from back_end.video_analyzer import StreamAnalyzer
from back_end.gopro_video_preprocessing import gopro_preprocess
from utils import write_csv

@click.command()
@click.option('--work_dir', default='.', help='video directory')
@click.option('--debug', default=False, is_flag=True, help='debug, visual mode')
def main(work_dir, debug):

    work_dir = Path(work_dir)
    video_file = work_dir / "full_video.mp4"
    calib_file = work_dir / "calib.json"
    assert calib_file.exists()

    gopro_preprocess(work_dir, video_file)

    with open(calib_file, "r") as cf:
        data = json.load(cf)

    st = StreamAnalyzer(video_file, data)
    for progress in st.run(debug=debug):
        print(f'\r\t->> progress: {progress * 100:.2f} %', end='')

    csv_lines = st.csv_info.tolist()
    csv_lines = sorted(np.asarray(csv_lines), key=lambda x: int(x[1]))

    write_csv(work_dir / "data.csv", csv_lines)

if __name__ == '__main__':
    main()
