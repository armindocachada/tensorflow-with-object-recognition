FROM armindocachada/tensorflow-object-detection-x86

RUN mkdir -p /data/videos/incoming
RUN pip3 install ephem

RUN echo 'cd /tensorflow/models/research && export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim:`pwd`/object_detection' >> /root/.bashrc
RUN echo 'export OBJECT_DETECTION_API_PATH=/tensorflow/models/research/object_detection' >> /root/.bashrc
COPY python /intruder-detector/
COPY config.ini /intruder-detector
WORKDIR /intruder-detector
COPY scripts/intruder_detection_service.sh /etc/init.d/intruder_detection_service
RUN chmod u+x  /etc/init.d/intruder_detection_service
COPY scripts/start.sh /root/start.sh
ENTRYPOINT ["/root/start.sh"]


RUN apt-get -y install libv4l-dev
RUN apt-get -y install libavcodec-dev libavformat-dev libavdevice-dev
RUN apt-get -y install wget
RUN apt-get -y install cmake


WORKDIR /root
RUN wget https://github.com/opencv/opencv/archive/3.4.4.zip
RUN unzip -o 3.4.4.zip
WORKDIR /root/opencv-3.4.4/build
RUN cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local  -D WITH_FFMPEG=ON -D WITH_TBB=ON -D WITH_GTK=ON -D WITH_V4L=ON -D WITH_OPENGL=ON -D WITH_CUBLAS=ON -DWITH_QT=OFF -DCUDA_NVCC_FLAGS="-D_FORCE_INLINES" ..
RUN make -j7
RUN make install