import pytest
import logging


# Configure logging for tests
@pytest.fixture(autouse=True)
def setup_logging():
    logging.basicConfig(level=logging.INFO)
