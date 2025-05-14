# Whalebone Microservice

A simple microservice with REST API endpoints for saving and retrieving user data.

## Requirements

- Python 3.10+
- Poetry
- SQLite (or another relational database)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Huge/whalebone-be-assessment whalebone-BE-assessment
cd whalebone-BE-assessment
```

2. Install dependencies using Poetry:
```bash
poetry install
```

## Configuration

The application uses environment variables for configuration. Create a `.env` file based on the provided `.env.example` template:

```bash
cp .env.example .env
```

Edit the `.env` file to customize your configuration. The available configuration options are:

- `PORT`: The port number to run the server on (default: 8000)
- `HOST`: The host address to bind to (default: 0.0.0.0)
- `DATABASE_URL`: The database connection URL (default: sqlite:///./test.db)
- `LOG_LEVEL`: The logging level (default: INFO)
- `ENVIRONMENT`: The environment type (development/production)

## Running the Application

Run the application using Poetry:

```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Or directly using uvicorn if you've activated the Poetry shell:

```bash
poetry shell
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once the application is running, you can access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing the Endpoints

### Save a user

```bash
curl -X POST http://localhost:8000/save \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "ext123",
    "name": "John Doe",
    "email": "john@example.com",
    "date_of_birth": "2020-01-01T12:12:34+00:00"
  }'
```

The response will include the ID of the saved user:

```json
{
  "id": "some-uuid",
  "message": "User saved successfully"
}
```

### Get a user by ID

```bash
curl http://localhost:8000/{id}
```

Replace `{id}` with the ID received from the save endpoint.

Response:

```json
{
  "external_id": "ext123",
  "name": "John Doe",
  "email": "john@example.com",
  "date_of_birth": "2020-01-01T12:12:34+00:00"
}
```

## Running Tests

Run the unit tests using pytest:

```bash
poetry run pytest tests/test_api.py
```

Run the integration tests:

```bash
poetry run pytest tests/test_integration.py
```

Run all tests:

```bash
poetry run pytest
```

## Docker

### Building the Docker Image

```bash
docker build -t whalebone-microservice .
```

### Running the Docker Container

```bash
docker run -p 8000:8000 whalebone-microservice
```

Now you can access the API at http://localhost:8000.

### Docker Compose (Optional)

If you prefer using Docker Compose, create a `docker-compose.yml` file with the following content:

```yaml
version: '3'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./app.db
```

Then run:

```bash
docker-compose up
```
