FROM python:3-alpine

WORKDIR /opt/app

RUN pip install requests

COPY main.py main.py

ENTRYPOINT [ "python", "main.py" ]
