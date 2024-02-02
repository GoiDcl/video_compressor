FROM python:3.11-slim

WORKDIR /compressor

COPY . .

RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apt update -y && apt-get install ffmpeg -y



