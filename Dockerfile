FROM python3.11-slim-bookworm

WORKDIR /compressor

COPY . .

RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt

