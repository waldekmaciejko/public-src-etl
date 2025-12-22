
1. [UNITY TESTS](#UNITY TESTS)
2. [Entire End 2 End test](#Entire End 2 End tes)

# GENERATE IMAGE


docker compose up -d                                        # compose file up
docker ps                                                   # show running containers
docker exec -it airflow-scheduler bash  
docker exec -it airflow-webserver bash                      # start console in container
docker compose up -d --build                                # rebuild container without stop services
docker compose up -d                                        # container start    
docker compose down                                         # stop containers
 
## linux you are not the owner
sudo chown -R username /path/to/directory

## commands called from console in airflow-scheduler
airflow info
airflow help
airflow cheat-sheet -v
exit                                                        # exit from container

## Fernet key generator

from cryptography.fernet import Fernet

fernet_key = Fernet.generate_key()
print(fernet_key.decode())

## modify docker-compose.yaml

docker compose up 
docker compose down

## key knowledge about airflow
https://airflow.apache.org/docs/apache-airflow/stable/howto/variable.html
https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html#declaring-a-dag
https://airflow.apache.org/docs/apache-airflow/stable/faq.html#what-s-the-deal-with-start-date
https://airflow.apache.org/docs/apache-airflow-providers-postgres/stable/_api/airflow/providers/postgres/hooks/postgres/index.html#module-airflow.providers.postgres.hooks.postgres

## access to the postgres table that works in separate container 
docker exec -it postgres psql -U yt_api_user -d elt_db

## important commands sql
\du         # shows users for this connestion
\l          # list of databases 
\dn         # schemas
\dt core.*  # all the tables under the schema
\q          * end the connection

## to see what is in db sql use dbviewer
## soda core to check data quality

# BUILD IMAGE
## 1. build image (after added requirements:
    # soda-core-postgres==3.3.14
    # pytest==8.3.2)

docker build -t waldekmaciejko/public-src-etl-image:1.0.1 .

## 2. push to docker repo
docker login -u username
docker push waldekmaciejko/public-src-etl-image:1.0.2

## 3. pull the image
docker compose pull 

## 4. recreate docker
## check IMAGE_TAG flag in .env and determine proper TAG
 docker compose up -d --force-recreate

## 5. check was the soda installed
 docker exec -it airflow-worker bash
 pip show soda-core-postgres


 # SODA
 ## write in console of container (first docker exec -it airflow-worker bash)
 soda --help

 ## 1. test connection to database
 ## https://docs.soda.io/data-source-reference/connect-postgres
 ## to connect have to create yaml file with connection details
 ## file should be created in include/soda/configuration.yml

data_source my_datasource:
  type: postgres
  host: ${POSTGRES_CONN_HOST}
  port: ${POSTGRES_CONN_PORT}
  username: ${ELT_DATABASE_USERNAME}
  password: ${ELT_DATABASE_PASSWORD}
  database: ${ELT_DATABASE_NAME}
  schema: ${SCHEMA}

  # 2. Test connection using configuration file

  soda test-connection -d my_datasource -c configuration.yml -V

  # 3. creat in include/soda/ file checks.yml

  https://docs.soda.io/soda-cl-overview

  # check.yml example file:
  # alignments are important

  checks for yt_api:
checks for yt_api:
  - missing_count("Video_ID") = 0
  - duplicate_count("Video_ID") = 0

  - likes_count_greater_than_vid_views = 0:
      name: Check for Like_Count greater than Video_Views
      likes_count_greater_than_vid_views query:
        SELECT COUNT(*)
        FROM yt_api
        WHERE "Comments_Count" > "Video_Views"

  - comments_count_greater_than_vid_views = 0:
      name: Check for Comments_Count greater than Video_Views
      comments_count_greater_than_vid_views query:
        SELECT COUNT(*)
        FROM yt_api
        WHERE "Comments_Count" > "Video_Views"

## 4. scan using this command
soda scan -d my_datasource -c /opt/airflow/include/soda/configuration.yml -v SCHEMA=core /opt/airflow/include/soda/checks.yml 

## 5. Integration data quality to the airflow
    1. create folder dataquality in dags
    2. create in folder file soda.py

## 6. integrate it with DAG
 create new DAG  dag_id="data_quality"

# UNITY TESTS <a name="UNITYTESTS"></a>
## 7. Functional testing

    unit
    integration
    end-2-end

    a) unit testing (pytest)
    https://docs.pytest.org/en/stable/reference/fixtures.html

    b) run in container's console 

    pytest -v tests/unit_test.py -k test_api_key
    pytest -v tests/unit_test.py -k test_channel_handle
    pytest -v tests/unit_test.py -k test_mock_postgres_conn
    pytest -v -s tests/unit_test.py -k test_dags_integrity
    pytest -v tests/integration_test.py -k test_youtube_api_response
    pytest -v tests/integration_test.py -k test_real_postgres_connection
  
# Entire End 2 End test
    ### call in runing container
    airflow dags test [name of dag] 
    
    airflow dags test produce_json
    airflow dags test update_db
    airflow dags test data_quality

    ## this process of automatic testing should be included in Continous Integration and Continous Deployment

# DAGs restructures 
We have no quarantee that they were run in the order we expect to
since sheduling is important.
We can achieve this using triggers
Remember to change the expected_task_counts in unit_test.py













