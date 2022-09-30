# pull the official docker image
FROM python:3.9.5-slim

# set work directory
WORKDIR /app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY odk_fieldmap/requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .