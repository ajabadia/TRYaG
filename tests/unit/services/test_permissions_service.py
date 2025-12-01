import pytest
from unittest.mock import patch, MagicMock
from services.permissions_service import has_permission, get_available_tabs

@pytest.fixture
def mock_role_repo():
    with patch('services.permissions_service.get_role_by_code') as mock_get_role:
        yield mock_get_role

@pytest.fixture
def mock_session_state():
    # Mocking st.session_state which is accessed via attribute access or get method
    # Since st.session_state is a proxy, we can mock it as a dict but we need to ensure
    # the code under test uses it correctly.
    # The code uses st.session_state.get("current_user")
    
    # We can patch st.session_state with a real dict, which has a .get method
    with patch('services.permissions_service.st.session_state', new_callable=dict) as mock_state:
        yield mock_state

def test_has_permission_no_user(mock_session_state):
    # Empty session state
    assert has_permission("admision") == False

def test_has_permission_superadmin(mock_session_state, mock_role_repo):
    mock_session_state["current_user"] = {"rol": "superadministrador"}
    mock_role_repo.return_value = {"code": "superadministrador", "permissions": {}}
    
    # Superadmin has access to everything
    assert has_permission("any_module", "any_action") == True

def test_has_permission_specific_role(mock_session_state, mock_role_repo):
    mock_session_state["current_user"] = {"rol": "enfermero"}
    mock_role_repo.return_value = {
        "code": "enfermero",
        "permissions": {
            "triaje": {"view": True, "edit": False},
            "admision": {"view": False}
        }
    }
    
    assert has_permission("triaje", "view") == True
    assert has_permission("triaje", "edit") == False
    assert has_permission("admision", "view") == False
    assert has_permission("unknown_module") == False

def test_get_available_tabs(mock_session_state, mock_role_repo):
    mock_session_state["current_user"] = {"rol": "administrativo"}
    mock_role_repo.return_value = {
        "code": "administrativo",
        "permissions": {
            "admision": {"view": True},
            "triaje": {"view": False},
            "configuracion": {"general": True} # Special case for config
        }
    }
    
    tabs = get_available_tabs()
    assert "📋 Admisión" in tabs
    assert "🩺 Triaje" not in tabs
    assert "⚙️ Configuración" in tabs
