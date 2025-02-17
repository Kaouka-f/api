FROM python:3.9-slim
WORKDIR /app
RUN apt-get update && apt-get install -y ffmpeg
COPY requirements.txt .
COPY src .