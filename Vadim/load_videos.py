import csv
import os
from collections import defaultdict
from random import random

import yt_dlp
import requests
from bs4 import BeautifulSoup
import json
import re

from yt_dlp import DownloadError

downloaded = set()


class YtDL(yt_dlp.YoutubeDL):
    def report_file_already_downloaded(self, file_name) -> None:
        downloaded.add(file_name.replace("data//", ""))
        super().report_file_already_downloaded(file_name)


def download_rutube_video(video_url, output_path=".", proxy=False):
    # Options for yt-dlp
    ydl_opts = {
        "format": "best[height<=360]",  # Download the best available quality
        "outtmpl": f"{output_path}/%(id)s.%(ext)s",  # Output file template
        "download-sections": "*0-300",  # trim first 5 min (300 sec)
    }
    if proxy:
       ydl_opts["proxy"] = "socks5://127.0.0.1:2080/"

    with YtDL(ydl_opts) as ydl:
        ydl.download([video_url])


def get_rutube_video_category(video_url):
    # Get the page content
    response = requests.get(video_url)
    if response.status_code != 200:
        print(f"Failed to fetch the page: {response.status_code}")
        return None

    # Parse the page content
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the JSON metadata in the "reduxState" JavaScript variable
    json_text = None
    for script in soup.find_all("script"):
        if "window.reduxState" in script.text:
            # Extract the JSON part of the script
            json_text = script.text.split("window.reduxState =")[-1].split(";</script>")[0].strip()
            break

    # If JSON data was not found, raise an error
    if json_text is None:
        raise ValueError("Failed to extract JSON data from the page. Please check the page structure.")

    # Fix any invalid escape characters in the JSON string
    json_text = re.sub(r"\\(?![\"\\bfnrtu])", r"\\\\",
                       json_text)  # Escape backslashes that are not part of a valid escape sequence

    # Try to remove any extra data after the first valid JSON object
    try:
        # Find where the valid JSON ends (by finding the last closing curly bracket)
        json_text = json_text[:json_text.rfind("}") + 1]
        video_data = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON: {e}")

    # Navigate to the category information and extract "id" and "name"
    try:
        category = list(video_data.get("video", {}).get("entities", {}).values())[0].get("video", {}).get("category", {})
        category_id = category["id"]
        category_name = category["name"]
        return soup.select(".video-pageinfo-container-module__videoTitleSectionHeader")[0].text, category_id, category_name
    except (KeyError, IndexError):
        print("Category information not found in the JSON data.")
        return None, None, None


from minio import Minio

client = Minio("storage.yandexcloud.net",
    access_key="YCAJESQqZUja9X-F1glArEPSY",
    secret_key="YCP6M_QUdKUF1XBlgz_hOWAlTkcMbnEUyLG5hsQv",
)

bucket = "rutube-tagging"
# url = f"https://rutube.ru/video/{audio_file[8:-4]}/"
# client.fput_object(bucket, "wtf.ignore", "../.gitignore")
# print(list(client.list_objects(bucket)))

# Example usage
if __name__ == "__main__":
    # Example Rutube video URLs

    with open('Categories - Лист1-Sunday.csv', newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        headers = next(reader)
        videos = list(reader)
    # videos =

    video_urls = [
        "https://rutube.ru/video/f6f630eec988b8103140e248ad164dfd/",
        "https://rutube.ru/video/87c767f226a766f5ac65c34c865aa245/",
        "https://rutube.ru/video/0133fcc895f14ae8a24e2dc4e4d7a097/",
        "https://rutube.ru/video/4615b206b0069c90de6eba852de7a0c1/",
        "https://rutube.ru/video/547d5c5884291fc3862e15301fb78f55/",
        "https://rutube.ru/video/42482199a11aeb37f6b0eed582174333/"
    ]
    def extract_video_id(video_url):
        return video_url.split("/")[-1]

    # Download each video
    results = {}
    with open('scraped_dataset.csv', 'w', newline='') as csvfile:
        fieldnames = ['url', 'parsed_category',  'manual_category_id','manual_category_en','manual_category', 's3_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        errors = []
        for row in videos:
            for i, url, in enumerate(row[6:16]):
                if not url.startswith('http'):
                    continue
                try:
                    print(f"Downloading: {i}")
                    print(f"Downloading: {i}")
                    print(f"Downloading: {i}")
                    try:
                        download_rutube_video(url, output_path="data/")
                    except DownloadError as e:
                        download_rutube_video(url, output_path="data/", proxy=True)

                    category = get_rutube_video_category(url)
                    video_id = url.split("/")[-2] + ".mp4"
                    local_path = os.path.join("data", video_id)
                    if video_id not in downloaded:
                        uploaded = client.fput_object(bucket, video_id, local_path)
                        s3_url = uploaded.location
                    else:
                        s3_url = f"https://storage.yandexcloud.net/rutube-tagging/{video_id}"
                    writer.writerow({'url': url,
                                     'parsed_category': category,
                                     'manual_category_id': row[0],
                                     'manual_category': row[3],
                                     'manual_category_en': row[4],
                                     's3_url': s3_url})

                    # results[url] = {"url": url, "s3_path": uploaded.location, "category": category, }

                except Exception as e:
                    errors.append((row, url))
                    ...

    print("DONE")