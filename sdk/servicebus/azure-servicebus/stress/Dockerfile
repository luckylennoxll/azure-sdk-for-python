# internal users should provide MCR registry to build via 'docker build . --build-arg REGISTRY="mcr.microsoft.com/mirror/docker/library/"'
# public OSS users should simply leave this argument blank or ignore its presence entirely
ARG REGISTRY="mcr.microsoft.com/mirror/docker/library/"
FROM ${REGISTRY}python:3.8-slim-buster
# Install if running off git branch
# RUN apt-get -y update && apt-get -y install git

WORKDIR /app

COPY ./scripts /app/stress/scripts

WORKDIR /app/stress/scripts
RUN pip install -r dev_requirements.txt