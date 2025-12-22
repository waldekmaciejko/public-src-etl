import sched
from numpy import extract
from sqlalchemy import desc
from tomlkit import date

from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

import pendulum
from datetime import datetime, timedelta
from api.video_from_yt_sts import (get_playlist_id,
                                    get_video_ids, 
                                    extract_video_data, 
                                    save_to_json) 

from datawarehouse.data_wh import staging_table, core_table
from dataquality.soda import yt_elt_data_quality

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
stating_schema = "staging"
core_schema = "core"

# exist three different ways do define a DAG
# **1. Using the DAG context manager**
# 2. Using the DAG as a decorator
# 3. Instantiating the DAG and setting the task's dag attribute

with DAG(
    dag_id="produce_json",
    default_args=default_args,
    description="A DAG to produce JSON fiele with raw data",
    catchup=False,                    
    schedule="0 14 * * *",
) as dag_produce:
    
    #define task
    playlist_id = get_playlist_id()
    video_ids = get_video_ids(playlist_id)
    extracted_data = extract_video_data(video_ids=video_ids)
    save_to_json_task = save_to_json(extrated_data=extracted_data)

    trigger_update_db = TriggerDagRunOperator(
        task_id="trigger_update_db",
        trigger_dag_id="update_db",
    )

    # define dependencies
    # order the task run from left to right
    playlist_id >> video_ids >> extracted_data >> save_to_json_task >> trigger_update_db


with DAG(
    dag_id="update_db",
    default_args=default_args,
    description="DAG to process JSON file and insert data into both staging and core schemas",
    catchup=False,                      # does not catchup dags from the past
    schedule=None,
) as dag_update:
    
    #define task
    update_staging = staging_table()
    update_core = core_table()

    trigger_data_quality = TriggerDagRunOperator(
        task_id="trigger_data_quality",
        trigger_dag_id="data_quality",
    )


    # define dependencies
    # order the task run from left to right
    update_staging >> update_core >> trigger_data_quality


with DAG(
    dag_id="data_quality",
    default_args=default_args,
    description="DAG to checks data quality using Soda SQL for both staging and core schemas",
    catchup=False,                      # does not catchup dags from the past
    schedule=None,
) as dag_quality:
    
    #define task
    soda_validate_staging = yt_elt_data_quality(stating_schema)
    soda_validate_core =  yt_elt_data_quality(core_schema)

    # define dependencies
    # order the task run from left to right
    soda_validate_staging >> soda_validate_core 