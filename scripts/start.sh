#!/bin/bash
cd /tensorflow/models/research && export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim:`pwd`/object_detection
export OBJECT_DETECTION_API_PATH=/tensorflow/models/research/object_detection
cd /intruder-detector && nohup python3 security_camera.py > /data/intruder_detection_service.out 2>&1 </dev/null &
tail -f /data/intruder_detection_service.out
