FROM python:3.8-buster

RUN adduser cors_scanner
RUN usermod -u 1000 cors_scanner

WORKDIR /home/cors_scanner

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY common common
COPY core core
COPY cors_scanner.py cors_scanner.py

RUN chown -R cors_scanner:cors_scanner ./
USER cors_scanner

ENTRYPOINT ["python", "cors_scanner.py"]