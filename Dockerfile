FROM armindocachada/tensorflow-object-detection-x86

RUN mkdir -p /data/videos/incoming

RUN echo 'cd /tensorflow/models/research && export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim:`pwd`/object_detection' >> /root/.bashrc
RUN echo 'export OBJECT_DETECTION_API_PATH=/tensorflow/models/research/object_detection' >> /root/.bashrc
COPY python /intruder-detector/
COPY config.ini /intruder-detector
WORKDIR /intruder-detector
COPY scripts/intruder_detection_service.sh /etc/init.d/intruder_detection_service
RUN chmod u+x  /etc/init.d/intruder_detection_service
COPY scripts/start.sh /root/start.sh



ENTRYPOINT ["/root/start.sh"]
