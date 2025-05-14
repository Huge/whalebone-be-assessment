import pytest
import subprocess
import time
import requests
import signal
import logging
import uuid # Added for generating UUIDs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="module")
def server_url():
    return "http://localhost:8000"

@pytest.fixture(scope="module")
def server(server_url):
    logger.info("Starting uvicorn server...")
    process = subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # More robust server readiness check
    max_wait_time = 30  # seconds
    poll_interval = 0.5  # seconds
    start_time = time.time()
    server_ready = False

    while time.time() - start_time < max_wait_time:
        try:
            # Use /docs as a health check, as it's a standard FastAPI endpoint
            # and root ("/") redirects to it.
            response = requests.get(f"{server_url}/docs", timeout=1)
            if response.status_code == 200:
                logger.info("Server started successfully and /docs is reachable.")
                server_ready = True
                break
        except requests.exceptions.ConnectionError:
            logger.info("Server not yet available, retrying...")
        except requests.exceptions.Timeout:
            logger.info("Server timed out on /docs, retrying...")
        time.sleep(poll_interval)

    if not server_ready:
        stdout, stderr = process.communicate(timeout=5) # Added timeout
        logger.error(f"Server stdout:\n{stdout.decode(errors='ignore')}")
        logger.error(f"Server stderr:\n{stderr.decode(errors='ignore')}")
        process.terminate() # Ensure process is killed if it started but isn't ready
        process.wait()
        pytest.fail(f"Server did not start properly within {max_wait_time} seconds.")

    yield server_url # Provide the URL to the tests

    logger.info("Stopping uvicorn server...")
    process.send_signal(signal.SIGTERM)
    try:
        process.wait(timeout=10) # Wait for graceful shutdown
    except subprocess.TimeoutExpired:
        logger.warning("Server did not terminate gracefully, killing.")
        process.kill()
        process.wait()
    logger.info("Server stopped.")

def test_user_save_and_get(server_url):
    # Generate a unique external_id for each test run to avoid conflicts if the database is not cleaned between runs:
    user_external_id = str(uuid.uuid4())
    user_data_to_save = {
        "external_id": user_external_id,
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "date_of_birth": "1990-05-15T10:30"
    }

    logger.info(f"Attempting to save user with external_id: {user_external_id}")
    save_response = requests.post(
        f"{server_url}/save",
        json=user_data_to_save
    )
    assert save_response.status_code == 200, \
        f"Failed to save user. Status: {save_response.status_code}, Response: {save_response.text}"

    #### CURRENTLY FAILING ON THIS weirdly: ####
    saved_data = save_response.json()
    assert "external_id" in saved_data, "Response JSON should contain 'external_id'"
    assert saved_data["external_id"] == user_external_id
    logger.info(f"User saved successfully: {saved_data}")

    # Test getting the user
    logger.info(f"Attempting to get user with external_id: {user_external_id}")
    get_response = requests.get(f"{server_url}/{user_external_id}")
    assert get_response.status_code == 200, \
        f"Failed to get user. Status: {get_response.status_code}, Response: {get_response.text}"

    retrieved_user_data = get_response.json()
    logger.info(f"User retrieved successfully: {retrieved_user_data}")

    assert retrieved_user_data["external_id"] == user_data_to_save["external_id"]
    assert retrieved_user_data["name"] == user_data_to_save["name"]
    assert retrieved_user_data["email"] == user_data_to_save["email"]
    # The API returns datetime as a string, ensure it matches.
    # Depending on precision, you might need more sophisticated datetime comparison.
    assert retrieved_user_data["date_of_birth"] == user_data_to_save["date_of_birth"]

    # Example of testing an update (if the same external_id means update)
    # The current API returns a message "Person with external_id ... already exists"
    # if you try to save with an existing external_id.
    # If it were an update, the logic would be different.
    # For this API, saving again with the same ID is not an update, but a handled conflict.
    logger.info(f"Attempting to save the same user again (expected conflict): {user_external_id}")
    save_again_response = requests.post(
        f"{server_url}/save",
        json=user_data_to_save
    )
    assert save_again_response.status_code == 200 # API returns 200 with a message
    save_again_data = save_again_response.json()
    assert "already exists" in save_again_data.get("message", "").lower()
    logger.info(f"Second save attempt (conflict) handled as expected: {save_again_data}")
