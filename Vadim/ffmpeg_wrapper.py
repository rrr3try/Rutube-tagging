import glob
import json
import logging
import os
import subprocess
import requests


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


def extract_audio(video_url, audio_path):
    run_command([
        f'ffmpeg', '-y', '-i', video_url, '-vn',
        '-c:a', 'copy', audio_path
    ])


def process_videos(video_dir):
    os.makedirs("./audio/", exist_ok=True)
    for video_file in glob.glob(video_dir + "/*.mp4"):
        audio_path = video_file.replace(".mp4", ".m4a").replace("trimed_videos/", "audio/")
        extract_audio(video_file, audio_path)

