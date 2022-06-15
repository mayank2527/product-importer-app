# Product Importer App

The Product Importer App offers endpoints to upload large csv and save it to database, track the progress of the upload and CRUD APIs on the product data. Also, supports creating webhooks that will get trigger on every product is created and updated using the CRUD endpoints.

## Run for development

- Rename the `.env.example` to `.env` in /app folder.
- Run `docker-compose up --build` to start up all the services in this repo.

## Creating a new migration

- `docker-compose run webapp flask db migrate`

## API endpoint

- `localhost:5000`
