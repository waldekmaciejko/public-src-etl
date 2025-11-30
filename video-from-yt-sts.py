from logging import raiseExceptions
import requests
import json
from dotenv import load_dotenv
import os

from streamlit import video


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

def get_video_ids(api_key: str,
            playlistID: str = "", 
            maxResults: int = 1) -> list:

    # playlistID = "UCNApG5p0QfZcTNodHaLMCOQ"
    video_ids = []
    pageToken = None

    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlistID}&key={api_key}"

    try:

        while True:
            url = base_url

            if pageToken:
                url += f"&pageToken={pageToken}"

            response = requests.get(url)
            response.raise_for_status()
            data = response.json() 

            for item in data.get('items', []):
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)   

            pageToken = data.get('nextPageToken')

            if not pageToken:
                break        
              

        return video_ids    

    except requests.exceptions.RequestException as e:
        raise e
    

def batch_list(video_id_lst, batch_size):

    for video_id in range(0, len(video_id_lst), batch_size):
        yield video_id_lst[video_id:video_id + batch_size]


def extract_video_data(video_ids,
                       YOUR_API_KEY,
                       max_results):

    extracted_data = []

    #batch_list(video_id_lst, batch_size)


    try:
        for batch in batch_list(video_ids, max_results):

            video_ids_str = ",".join(batch)

            #print(video_ids_str)

            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={YOUR_API_KEY}"

            response = requests.get(url)
            response.raise_for_status()
            data = response.json() 

            for item in data.get('items', []):
                video_id = item['id']
                snippet = item['snippet']
                statistics = item['statistics']
                contentDetails = item['contentDetails'] 

                video_data = {
                    "video_id":video_id,
                    "title": snippet['title'],
                    "publishedAt": snippet['publishedAt'],
                    "duration": contentDetails['duration'],
                    "viewCount": statistics.get('viewCount', None),
                    "likeCount": item['statistics'].get('likeCount', 0),
                    "commentCount": item['statistics'].get('commentCount', 0)                 
                }
                extracted_data.append(video_data)

        return extracted_data
    
    except requests.exceptions.RequestException as e:
        raise e 


if __name__ == "__main__":

    load_dotenv(override=True, verbose=True, dotenv_path=".env")
    api_key = os.getenv("API_KEY")

    CHANNEL_HANDLE = "realAndromeda"

    playlistID = get_playlist_id(channelHandle=CHANNEL_HANDLE, 
                                 api_key=api_key)

    video_ids = get_video_ids(api_key=api_key,
                                playlistID=playlistID,
                                maxResults=5)
    
    a = extract_video_data(video_ids=video_ids,
                           YOUR_API_KEY=api_key,
                           max_results=1)

    print(a)





