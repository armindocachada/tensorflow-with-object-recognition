# tensorflow-with-object-recognition

1. Build docker container
docker build -t armindocachada/tensorflow-with-object-recognition .

2. Start docker container

Pass the -v to share the folder with the docker container in which the camera's surveillance files will be available. You need read/write access to the folder.

Pass the -p to expose the port to access the jupyter notebook

docker run -i -t -d -p 8888:8888 -v <NAS FOLDER WITH VIDEOS>:/data/videos/incoming armindocachada/tensorflow-with-object-recognition /bin/bash



 docker exec -it <CONTAINER ID> /bin/bash -c "export COLUMNS=tput cols; export LINES=tput lines; exec bash"

