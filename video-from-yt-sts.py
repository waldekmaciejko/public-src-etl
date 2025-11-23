from logging import raiseExceptions
import requests
import json
from dotenv import load_dotenv
import os


def get_playlist_id(channelHandle: str,
                    api_key: str) -> str:
    
    CHANNEL_HANDLE = channelHandle
    API_KEY = api_key
    
    url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"
    
    try: 
        response = requests.get(url)

        response.raise_for_status()

        data = response.json()
        #print(json.dumps(data, indent=4))

        channel_items = data['items'][0]
        channel_playlist = channel_items['contentDetails']['relatedPlaylists']['uploads']
        #print(channel_playlist)

        return channel_playlist
    
    except requests.exceptions.RequestException as e:
        
        raise e


if __name__ == "__main__":

    load_dotenv(dotenv_path='./.env', override=True)
    API_KEY = os.getenv("API_KEY")

    CHANNEL_HANDLE = "realAndromeda"

    print(get_playlist_id(CHANNEL_HANDLE, API_KEY))



