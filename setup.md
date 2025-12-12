
# Generate image

docker build -t waldekmaciejko/public-src-etl-image:1.0.0 . 
docker compose up -d                                        # compose file up
docker ps                                                   # show running containers
docker exec -it airflow-scheduler bash  
docker exec -it airflow-webserver bash                      # start console in container
docker compose up -d --build                                # rebuild container without stop services
docker compose up -d                                        # container start    
docker compose down                                         # stop containers
 
# linux you are not the owner
sudo chown -R username /path/to/directory

# commands called from console in airflow-scheduler
airflow info
airflow help
airflow cheat-sheet -v
exit                                                        # exit from container

# Fernet key generator

from cryptography.fernet import Fernet

fernet_key = Fernet.generate_key()
print(fernet_key.decode())

# modify docker-compose.yaml

docker compose up 
docker compose down

# key knowledge about airflow
https://airflow.apache.org/docs/apache-airflow/stable/howto/variable.html
https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html#declaring-a-dag
https://airflow.apache.org/docs/apache-airflow/stable/faq.html#what-s-the-deal-with-start-date
