FROM python:3.9.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

COPY ./src/marketdata /app

ENTRYPOINT [ "python3", "/app/main.py" ]