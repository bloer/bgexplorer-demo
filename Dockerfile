FROM python:3.10-slim

ADD . /app
WORKDIR /app

RUN apt-get update && apt-get install -y git && apt-get clean
RUN python3 -m pip install -r requirements.txt --no-cache-dir

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "-t", "600", "-w", "4", \
     "app:create_app('config.docker.py')"]
