Address Service
-
The Address Service lets you manage all your addresses.

The service comes with interactive Swagger docs (see below for details).

## System requirements
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Poetry](https://python-poetry.org/) (optional)

## Interact with the API

All dependencies and setup steps are performed through Docker Compose.

You should be able to get a running service with the following command:
```bash
docker compose up
```

### Setup a user and OAuth Client credentials

1. With docker compose running, create a superuser `admin`:
```
docker compose exec app ./manage.py createsuperuser --email admin@example.com --username admin
```

2. Login using your credentials [http://localhost:8000/admin/login/](http://localhost:8000/admin/login/).

3. Create an OAuth2 application [http://localhost:8000/oauth/applications/register/](http://localhost:8000/oauth/applications/register/)

    Choose `Confidential` and `Resource owner password-based`. Make sure to copy your credentials.

4a. Query the API with Swagger UI (see below)

4b. Query the API with curl

```bash
# Get an access token (valid for 10 minutes)
curl -X POST -d "grant_type=password&username=admin&password=<password>" -u"<client_id>:<client_secret>" http://localhost:8000/oauth/token/

#  {"access_token": "<token>", "expires_in": 36000, "token_type": "Bearer", "scope": "read write delete addresses", "refresh_token": "<refresh-token>"}
# Authorize using the token
curl -H 'Authorization: Bearer <token>' http://localhost:8000/api/addresses/
```

## Documentation site (Swagger UI)

See for a complete overview of endpoints the generated [API documentation](http://localhost:8000/docs/).

The UI also allows simple API interactions. Make sure to provide your client and user credentials before under "Authorize".

## Development

### Running the tests

At the moment only functional tests make sense as we only need to ensure the libraries are well configured and
integrated. You can find them here `tests/functional/test_addresses_api.py`.

Running the test suite can be done through Docker Compose.
```bash
docker compose exec app pytest .
```

### Local development setup
```bash
poetry install
pre-commit install  # Automatic linting and code quality check at each commit
```