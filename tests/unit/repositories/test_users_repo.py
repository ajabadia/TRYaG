import pytest
from unittest.mock import MagicMock, patch
from bson import ObjectId
from db.repositories.users import UsersRepository

@pytest.fixture
def mock_db_users(mock_db):
    return mock_db.users

@pytest.fixture
def users_repo(mock_db):
    # Patch get_database inside the class init or module
    with patch('db.repositories.users.get_database', return_value=mock_db):
        return UsersRepository()

def test_create_user(users_repo, mock_db_users):
    user_data = {"username": "testuser", "rol": "medico"}
    user_id = users_repo.create_user(user_data)
    
    assert user_id is not None
    
    # Check insertion
    saved_user = mock_db_users.find_one({"_id": ObjectId(user_id)})
    assert saved_user is not None
    assert saved_user["username"] == "testuser"
    assert saved_user["activo"] == True
    assert "created_at" in saved_user

def test_get_by_username(users_repo, mock_db_users):
    mock_db_users.insert_one({"username": "found"})
    
    user = users_repo.get_by_username("found")
    assert user is not None
    assert user["username"] == "found"

def test_get_users_by_role(users_repo, mock_db_users):
    mock_db_users.insert_many([
        {"username": "u1", "rol": "enfermero", "activo": True},
        {"username": "u2", "rol": "enfermero", "activo": True},
        {"username": "u3", "rol": "medico", "activo": True}
    ])
    
    users = users_repo.get_users_by_role("enfermero")
    assert len(users) == 2
    assert all(u["rol"] == "enfermero" for u in users)
