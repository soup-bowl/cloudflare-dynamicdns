FROM python:3-alpine

WORKDIR /opt/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY cddns cddns
COPY run.py .

ENTRYPOINT [ "python", "run.py" ]
