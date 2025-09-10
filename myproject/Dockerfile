# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# System deps for psycopg2 + netcat for waiting for DB
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev gcc netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*
    
RUN apt-get update && apt-get install -y postgresql-client


WORKDIR /code

# Install python deps
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . /code/

# entrypoint script
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
