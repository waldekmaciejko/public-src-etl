
# Generate image

docker build -t waldekmaciejko/public-src-etl-image:1.0.0 . 
docker compose up -d                                        # compose file up
docker ps                                                   # show running containers
docker exec -it airflow-scheduler bash                      # start console in container
docker compose up -d --build                                # rebuild container without stop services
docker compose down                                         # stop containers
 


# commands called from console in airflow-scheduler
airflow info
airflow help
airflow cheat-sheet -v
exit                                                        # exit from container

# Fernet key generator

from cryptography.fernet import Fernet

fernet_key = Fernet.generate_key()
print(fernet_key.decode())