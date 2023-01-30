import subprocess
import os

CALIB_JSON = 'calib.json'
DATA_CSV = 'data.csv'
concat_file = "to_concat.txt"

ffmpeg_trim = ["ffmpeg", "-i", "**in_vid**", "-ss", "60", "-c", "copy", "**out_vid**", "-y"]
ffmpeg_concat = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", "**concat_file**", "-c", "copy", "**out_concat_vid**", "-y"]

def do_ffmpeg_command(cmd):
    subprocess.run(cmd)

def gopro_preprocess(in_dir, full_video_path):
    yield 0.1

    if not full_video_path.exists():
        print("using ffmpeg to concat recorded videos")
        videos = sorted(in_dir.files("*.MP4"))
        first_video_trim_name = in_dir / videos[0].replace(".MP4", "_trim_.MP4")

        print("trim 60 sec of the first video")
        command = ffmpeg_trim[:]
        command[2] = in_dir / videos[0]
        command[7] = first_video_trim_name
        yield 0.2
        do_ffmpeg_command(command)
        yield 0.4

        print("concatenating videos...")
        with open(in_dir / concat_file, "w") as f:
            videos[0] = first_video_trim_name
            for v in videos:
                f.write("file ")
                if os.name == "nt":
                    f.write("'" + v.abspath() + "'" + "\n")
                else:
                    f.write(v.abspath() + "\n")

        command = ffmpeg_concat[:]
        command[6] = in_dir / concat_file
        command[9] = full_video_path
        yield 0.6
        do_ffmpeg_command(command)

    yield 1