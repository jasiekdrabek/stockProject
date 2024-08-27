#!/bin/bash
LOCAL_IP=host.docker.internal
locust --host=http://$LOCAL_IP:8080