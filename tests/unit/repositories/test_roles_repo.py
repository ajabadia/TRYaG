import pytest
from unittest.mock import MagicMock, patch
from db.repositories.roles import RolesRepository, DEFAULT_ROLES

@pytest.fixture
def mock_db_roles(mock_db):
    return mock_db.roles

@pytest.fixture
def roles_repo(mock_db):
    with patch('db.repositories.roles.get_database', return_value=mock_db):
        return RolesRepository()

def test_initialize_defaults(roles_repo, mock_db_roles):
    # Should be called on init if empty
    # In mongomock, count_documents({}) is 0 initially, so defaults are inserted
    
    # Verify defaults are inserted by checking the collection count
    assert mock_db_roles.count_documents({}) == len(DEFAULT_ROLES)

def test_get_role_by_code(roles_repo, mock_db_roles):
    # Insert data first
    mock_db_roles.insert_one({"code": "admin", "nombre": "Admin"})
    
    role = roles_repo.get_role_by_code("admin")
    assert role is not None
    assert role["nombre"] == "Admin"

def test_create_role_success(roles_repo, mock_db_roles):
    # Setup: Role does not exist (collection is empty or doesn't have this code)
    
    new_role = {"code": "new_role", "nombre": "New Role"}
    success = roles_repo.create_role(new_role)
    
    assert success == True
    assert mock_db_roles.find_one({"code": "new_role"}) is not None

def test_create_role_duplicate(roles_repo, mock_db_roles):
    # Setup: Role exists
    mock_db_roles.insert_one({"code": "existing", "nombre": "Existing"})
    
    new_role = {"code": "existing", "nombre": "Duplicate"}
    success = roles_repo.create_role(new_role)
    
    assert success == False
    # Verify it wasn't overwritten
    assert mock_db_roles.find_one({"code": "existing"})["nombre"] == "Existing"
