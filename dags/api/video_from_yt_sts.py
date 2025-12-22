from logging import raiseExceptions
from numpy import save
import requests
import json
# from dotenv import load_dotenv
# import os
from datetime import date 
from airflow.decorators import task
from airflow.models import Variable
#from streamlit import video

#load_dotenv(override=True, verbose=True, dotenv_path=".env")

#CHANNEL_HANDLE = "realAndromeda"

API_KEY = Variable.get("API_KEY")
CHANNEL_HANDLE = Variable.get("CHANNEL_HANDLE")
maxResults = 50

import logging
logger = logging.getLogger(__name__)

@task
def get_playlist_id() -> str:
    
    #CHANNEL_HANDLE = channelHandle
    #API_KEY=""   
    #CHANNEL_HANDLE="MrBeast"

   
    try: 
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"

        response = requests.get(url)

        response.raise_for_status()

        data = response.json()
        #print(json.dumps(data, indent=4))

        channel_items = data['items'][0]
        channel_playlist = channel_items['contentDetails']['relatedPlaylists']['uploads']
        #print(channel_playlist)

        return channel_playlist
        #return "UUX6OQ3DkcsbYNE6H8uQQuVA"
    
    except requests.exceptions.RequestException as e:
        
        raise e

@task
def get_video_ids(playlistID) -> list:

    # playlistID = "UCNApG5p0QfZcTNodHaLMCOQ"
    video_ids = []
    pageToken = None
    maxResults = 10

    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlistID}&key={API_KEY}"

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
    

@task
def extract_video_data(video_ids):

    def batch_list(video_id_lst, batch_size):

        for video_id in range(0, len(video_id_lst), batch_size):
            yield video_id_lst[video_id:video_id + batch_size]

    extracted_data = []
    max_results = 10

    #batch_list(video_id_lst, batch_size)


    try:
        for batch in batch_list(video_ids, max_results):

            video_ids_str = ",".join(batch)

            #print(video_ids_str)

            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={API_KEY}"

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

@task
def save_to_json(extrated_data):

    file_path = f"./data/yt_src_{date.today()}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(extrated_data, f, indent=4, ensure_ascii=False)

    return file_path



if __name__ == "__main__":

    print('ok')

    # load_dotenv(override=True, verbose=True, dotenv_path=".env")
    # api_key = os.getenv("API_KEY")

    # #CHANNEL_HANDLE = "realAndromeda"
    # channel_handel = "MrBeast"

    # playlistID = get_playlist_id(channelHandle=channel_handel, 
    #                              api_key=api_key)

    # video_ids = get_video_ids(api_key=api_key,
    #                             playlistID=playlistID,
    #                             maxResults=5)
    
    # video_data = extract_video_data(video_ids=video_ids,
    #                        YOUR_API_KEY=api_key,
    #                        max_results=1)

    # save_to_json(video_data)





