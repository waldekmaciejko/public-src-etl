import sched
from numpy import extract
from sqlalchemy import desc
from tomlkit import date
from airflow import DAG
import pendulum
from datetime import datetime, timedelta
from api.video_from_yt_sts import (get_playlist_id,
                                    get_video_ids, 
                                    extract_video_data, 
                                    save_to_json) 

local_tz = pendulum.timezone("Europe/Warsaw")

default_args={
        "owner": "dataengineers",
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
        "email": "w.maciej.git@gmail.com",
        #"retries": 1,
        "retry_delay": timedelta(minutes=5),
        "max_active_runs": 1,
        "dagrun_timeout": timedelta(minutes=60),
        "start_date": datetime(2025, 1, 1, tzinfo=local_tz),
        # 'queue': 'bash_queue',
        # 'pool': 'backfill',
        # 'priority_weight': 10,
        # 'end_date': datetime(2016, 1, 1),
        # 'wait_for_downstream': False,
        # 'execution_timeout': timedelta(seconds=300),
        # 'on_failure_callback': some_function, # or list of functions
        # 'on_success_callback': some_other_function, # or list of functions
        # 'on_retry_callback': another_function, # or list of functions
        # 'sla_miss_callback': yet_another_function, # or list of functions
        # 'on_skipped_callback': another_function, #or list of functions
        # 'trigger_rule': 'all_success'
    }

with DAG(
    dag_id="produce_json",
    default_args=default_args,
    description="A DAG to produce JSON fiele with raw data",
    schedule="0 14 * * *",
    catchup=False                      # does not catchup dags from the past
) as dag:
    
    #define task
    playlist_id = get_playlist_id()
    video_ids = get_video_ids(playlist_id)
    extracted_data = extract_video_data(video_ids=video_ids)
    save_to_json_task = save_to_json(extrated_data=extracted_data)

    # define dependencies
    # order the task run from left to right
    playlist_id >> video_ids >> extracted_data >> save_to_json_task
     
