FROM python:3-alpine

WORKDIR /opt/app

RUN pip install --no-cache-dir requests

COPY cddns cddns

ENTRYPOINT [ "python", "-m", "cddns" ]
