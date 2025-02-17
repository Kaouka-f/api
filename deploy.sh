#!/bin/sh

docker build -t proxy .
docker tag proxy 159091/proxy:1.0
docker push 159091/proxy:1.0