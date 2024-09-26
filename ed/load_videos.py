import yt_dlp
import requests
from bs4 import BeautifulSoup
import json
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd


SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SHEET_ID = '1oP-63iuYepvQrkXv-fhPP7oN5fanL6ufaPOdfr2pMm8'
RANGE_NAME = 'Sheet1!A1:P47'  # Adjust range as needed


def get_google_sheet_data(sheet_id, range_name, credentials_file):
    """Fetches data from Google Sheets."""
    credentials = service_account.Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()

    result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
        return None
    return pd.DataFrame(values[1:], columns=values[0])  # Return a pandas DataFrame


def download_rutube_video(video_url, output_path='.'):
    # Options for yt-dlp
    ydl_opts = {
        'format': 'best[height<=360]',  # Download the best available quality
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',  # Output file template
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])


def get_rutube_video_category(video_url):
    # Get the page content
    response = requests.get(video_url)
    if response.status_code != 200:
        print(f"Failed to fetch the page: {response.status_code}")
        return None

    # Parse the page content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the JSON metadata in the 'reduxState' JavaScript variable
    json_text = None
    for script in soup.find_all('script'):
        if 'window.reduxState' in script.text:
            # Extract the JSON part of the script
            json_text = script.text.split('window.reduxState =')[-1].split(';</script>')[0].strip()
            break

    # If JSON data was not found, raise an error
    if json_text is None:
        raise ValueError("Failed to extract JSON data from the page. Please check the page structure.")

    # Fix any invalid escape characters in the JSON string
    json_text = re.sub(r'\\(?![\"\\bfnrtu])', r'\\\\',
                       json_text)  # Escape backslashes that are not part of a valid escape sequence

    # Try to remove any extra data after the first valid JSON object
    try:
        # Find where the valid JSON ends (by finding the last closing curly bracket)
        json_text = json_text[:json_text.rfind('}') + 1]
        video_data = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON: {e}")

    # Navigate to the category information and extract 'id' and 'name'
    try:
        category = list(video_data.get('video', {}).get('entities', {}).values())[0].get('video', {}).get('category', {})
        category_id = category['id']
        category_name = category['name']
        return category_id, category_name
    except KeyError:
        print("Category information not found in the JSON data.")
        return None, None


# Example usage
if __name__ == "__main__":
    # Example Rutube video URLs
    video_urls = [
        'https://rutube.ru/video/f6f630eec988b8103140e248ad164dfd/',
        'https://rutube.ru/video/87c767f226a766f5ac65c34c865aa245/',
        'https://rutube.ru/video/0133fcc895f14ae8a24e2dc4e4d7a097/',
        'https://rutube.ru/video/4615b206b0069c90de6eba852de7a0c1/',
        'https://rutube.ru/video/547d5c5884291fc3862e15301fb78f55/',
        'https://rutube.ru/video/42482199a11aeb37f6b0eed582174333/'
    ]

    # Download each video
    for url in video_urls:
        print(f"Downloading: {url}")
        # download_rutube_video(url, output_path='data/')
        category = get_rutube_video_category(url)
        if category:
            print(f"Video category: {category}")
        else:
            print("Failed to retrieve video category.")
        print("Download complete.")