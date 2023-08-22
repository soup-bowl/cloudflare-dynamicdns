FROM python:3-alpine

WORKDIR /opt/app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY cddns cddns

ENTRYPOINT [ "python", "-m", "cddns" ]
