## Development

### Config:

    cp .env.example .env

Update the .env file with the desired settings.

### Start Services:

    docker compose up --build

### Debugging

Open tty to container

    docker attach field-map-odk-web-1

Add debug line in code

    import pdb;pdb.set_trace()

When this line is reached in the code then the attached tty window will 
become interactive with pdb.

Access database (psql):

    docker exec -it field-map-odk-db-1 psql -U fmtm fmtm

## Production

### Config:

    cp .env.example .env

Update the .env file with the desired settings.

### Start services:

    docker compose -f docker-compose.prod.yml up -d --build

### Access database:

    docker compose exec db psql --username=fmtm --dbname=fmtm

## Testing

    pip install -r odk_fieldmap/requirements.txt
    python -m pytest
