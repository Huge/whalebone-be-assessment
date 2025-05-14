FROM python:3.10-slim

WORKDIR /app

# Install poetry
RUN pip install poetry==1.7.0

# Copy poetry configuration files
COPY pyproject.toml poetry.lock* ./

# Copy application code early for poetry install
COPY app ./app

# Configure poetry to not use a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --only main


# Expose the port the app will run on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
