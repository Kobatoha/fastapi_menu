FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /fastapi_menu
COPY .env .

ENV DB_URL="postgresql://user:password@db:5432/dbname"
ENV POSTGRES_DB=dbname
ENV POSTGRES_USER=user
ENV POSTGRES_PASSWORD=password
ENV POSTGRES_HOST=db
ENV POSTGRES_PORT=5432

RUN echo "CREATE DATABASE dbname;" > init.sql

COPY init.sql /docker-entrypoint-initdb.d/
EXPOSE 80


CMD ["uvicorn", "main:app", "--reload"]