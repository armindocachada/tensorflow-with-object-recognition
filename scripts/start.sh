#!/bin/bash

service intruder_detection_service start
tail -f /data/intruder_detection_service.out
