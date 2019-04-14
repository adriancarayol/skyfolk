import subprocess


def create_thumbnail_video(video_file_path, output_name):
    process = subprocess.run(
        "ffmpeg -y -i '{input}' -ss 00:00:01.000 -vframes 1 -f image2 '{output}'".format(
            input=video_file_path, output=output_name
        ),
        shell=True,
    ).returncode
