#!/bin/bash

cd /intruder-detector && nohup python3 security_camera.py > /data/intruder_detection_service.out 2>&1 </dev/null &
tail -f /data/intruder_detection_service.out
