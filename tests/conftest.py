import pytest
import mongomock
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

@pytest.fixture
def mock_mongo_client():
    """Returns a mongomock MongoClient."""
    return mongomock.MongoClient()

@pytest.fixture
def mock_db(mock_mongo_client):
    """Returns a mongomock Database."""
    return mock_mongo_client.db

@pytest.fixture(autouse=True)
def patch_mongo_connection(mock_mongo_client, mock_db):
    """
    Automatically patch db.connection.get_client and get_database
    for all tests. Patches both 'src.db' and 'db' to cover different import styles.
    """
    with patch('db.connection.get_client', return_value=mock_mongo_client), \
         patch('db.connection.get_database', return_value=mock_db), \
         patch('db.connection.get_client', return_value=mock_mongo_client), \
         patch('db.connection.get_database', return_value=mock_db):
        yield

@pytest.fixture
def mock_streamlit():
    """Mocks streamlit module to prevent errors when importing UI components."""
    with patch('streamlit.secrets', {}), \
         patch('streamlit.session_state', {}), \
         patch('streamlit.error'), \
         patch('streamlit.warning'), \
         patch('streamlit.info'), \
         patch('streamlit.success'):
        yield
