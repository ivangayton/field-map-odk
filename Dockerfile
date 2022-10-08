# pull the official docker image
FROM python:3.10.7-slim

# set work directory
WORKDIR /app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install postgresql package requirements
RUN apt update && \
    apt install -y libpq-dev gcc

# install dependencies
COPY odk_fieldmap/requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .
