FROM python:3.8

WORKDIR /app
COPY . .
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y
RUN pip install --no-cache-dir --upgrade -r requirements.txt
CMD uvicorn main:app --host 0.0.0.0 --port ${USE_PORT}