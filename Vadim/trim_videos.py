import glob
import json
import logging
import os
import subprocess
import time

import requests
from tqdm import tqdm

from dataset.load_videos import client


def run_command(command: list[str]):
    """ command example ["ffmpeg", "Hello, World!"] """

    process = subprocess.Popen(command,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        output = stdout.decode('utf-8').strip()
    else:
        output = stderr.decode()
        logging.error(output)

    return process.returncode, output


def trim_video(video_url, output_path):
    """ffmpeg -ss 00:01:00 -to 00:02:00 -i input.mp4 -c copy output.mp4"""
    run_command([
        f'ffmpeg', '-y', '-i', video_url, '-ss', '00:00:00', '-to', '00:05:00',
        '-c', 'copy', output_path
    ])


if __name__ == '__main__':
    os.makedirs("trimed_videos", exist_ok=True)
    d = lambda: 0
    bucket = "rutube-tagging"
    # url = f"https://rutube.ru/video/{audio_file[8:-4]}/"
    for video_path in tqdm(glob.glob('trimed_videos/*.mp4')):
        video_id = video_path.split('/')[-1]
        uploaded = client.fput_object(bucket, video_id, video_path)

        # d()
        # print()
        # output_path = video_path.replace('data/', 'trimed_videos/')
        # trim_video(video_path, output_path)
        # os.remove(video_path)

