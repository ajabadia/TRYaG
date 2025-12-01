import pytest
from datetime import datetime, date, time
from unittest.mock import MagicMock, patch
from src.services.staff_assignment_service import (
    get_current_user_assignment,
    validate_shift_assignment
)

@pytest.fixture
def mock_repos():
    with patch('src.services.staff_assignment_service.get_users_repository') as mock_users_repo, \
         patch('src.services.staff_assignment_service.get_turnos_repository') as mock_turnos_repo:
        yield mock_users_repo, mock_turnos_repo

def test_get_current_user_assignment_fixed_only(mock_repos):
    mock_users_repo, mock_turnos_repo = mock_repos
    
    # Setup: User has fixed assignment, no shifts
    mock_users_repo.return_value.get_by_id.return_value = {"sala_asignada": "ROOM_A"}
    mock_turnos_repo.return_value.get_user_shifts.return_value = []
    
    result = get_current_user_assignment("user1")
    assert result == "ROOM_A"

def test_get_current_user_assignment_shift_active(mock_repos):
    mock_users_repo, mock_turnos_repo = mock_repos
    
    # Setup: User has fixed ROOM_A, but active shift in ROOM_B
    mock_users_repo.return_value.get_by_id.return_value = {"sala_asignada": "ROOM_A"}
    
    mock_shift = MagicMock()
    mock_shift.sala_code = "ROOM_B"
    mock_shift.horario_inicio = time(9, 0)
    mock_shift.horario_fin = time(17, 0)
    
    mock_turnos_repo.return_value.get_user_shifts.return_value = [mock_shift]
    
    # Test at 10:00 (inside shift)
    ref_time = datetime.combine(date.today(), time(10, 0))
    result = get_current_user_assignment("user1", reference_datetime=ref_time)
    
    assert result == "ROOM_B"

def test_get_current_user_assignment_shift_inactive(mock_repos):
    mock_users_repo, mock_turnos_repo = mock_repos
    
    # Setup: User has fixed ROOM_A, shift in ROOM_B (ended)
    mock_users_repo.return_value.get_by_id.return_value = {"sala_asignada": "ROOM_A"}
    
    mock_shift = MagicMock()
    mock_shift.sala_code = "ROOM_B"
    mock_shift.horario_inicio = time(9, 0)
    mock_shift.horario_fin = time(12, 0)
    
    mock_turnos_repo.return_value.get_user_shifts.return_value = [mock_shift]
    
    # Test at 13:00 (outside shift)
    ref_time = datetime.combine(date.today(), time(13, 0))
    result = get_current_user_assignment("user1", reference_datetime=ref_time)
    
    assert result == "ROOM_A"

def test_validate_shift_assignment_conflict(mock_repos):
    mock_users_repo, mock_turnos_repo = mock_repos
    
    # Setup: Existing shift 9-12
    existing_shift = MagicMock()
    existing_shift.horario_inicio = time(9, 0)
    existing_shift.horario_fin = time(12, 0)
    existing_shift.sala_code = "ROOM_A"
    
    mock_turnos_repo.return_value.get_user_shifts.return_value = [existing_shift]
    
    # Try to add shift 11-13 (overlap)
    valid, msg = validate_shift_assignment(
        "user1", "ROOM_B", date.today(), time(11, 0), time(13, 0)
    )
    
    assert valid == False
    assert "Conflicto de horario" in msg
