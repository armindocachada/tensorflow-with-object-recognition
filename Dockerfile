FROM macgyvertechnology/tensorflow
RUN pip install Cython
RUN pip install jupyter
RUN pip install matplotlib
RUN pip install slackclient
RUN apt-get -y install python-pil python-lxml python-tk python-opencv
COPY tensorflow-models /tensorflow/models
RUN mkdir -p /data/videos/incoming
RUN mkdir -p /data/videos/archive
COPY example_videos/* /data/videos/incoming/
COPY object_detection_tutorial.* /tensorflow/models/research/object_detection/
RUN curl -OL https://github.com/google/protobuf/releases/download/v3.5.1/protoc-3.5.1-linux-x86_64.zip
RUN unzip -o protoc-3.5.1-linux-x86_64.zip -d /usr/local bin/protoc
RUN cd /tensorflow/models/research && protoc object_detection/protos/*.proto --python_out=.
RUN cd /tensorflow/models/research && export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim && python object_detection/builders/model_builder_test.py

#rm -f $PROTOC_ZIP



#protoc research/object_detection/protos/*.proto --python_out=.