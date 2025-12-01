import pytest
from datetime import datetime, timedelta
from src.services.queue_manager import (
    calculate_priority_score, 
    sort_queue, 
    get_wait_time_alert
)

def test_calculate_priority_score_levels():
    # Lower score = Higher priority
    p1 = {"nivel_triaje": "Nivel I (Rojo)", "wait_start": datetime.now()}
    p2 = {"nivel_triaje": "Nivel III (Amarillo)", "wait_start": datetime.now()}
    
    s1 = calculate_priority_score(p1)
    s2 = calculate_priority_score(p2)
    
    assert s1 < s2  # Red should be lower score (higher priority) than Yellow

def test_calculate_priority_score_wait_time():
    now = datetime.now()
    # Same level, different wait times
    p1 = {"nivel_triaje": "Nivel III", "wait_start": now - timedelta(minutes=10)}
    p2 = {"nivel_triaje": "Nivel III", "wait_start": now - timedelta(minutes=30)}
    
    s1 = calculate_priority_score(p1)
    s2 = calculate_priority_score(p2)
    
    assert s2 < s1 # Longer wait (30m) should have lower score (higher priority)

def test_sort_queue():
    now = datetime.now()
    patients = [
        {"id": 1, "nivel_triaje": "Nivel V", "wait_start": now},
        {"id": 2, "nivel_triaje": "Nivel I", "wait_start": now},
        {"id": 3, "nivel_triaje": "Nivel III", "wait_start": now}
    ]
    
    sorted_p = sort_queue(patients)
    
    assert sorted_p[0]["id"] == 2 # Level I
    assert sorted_p[1]["id"] == 3 # Level III
    assert sorted_p[2]["id"] == 1 # Level V

def test_get_wait_time_alert():
    now = datetime.now()
    
    # Red level thresholds: 5m warn, 10m crit
    p_normal = {"nivel_triaje": "Nivel I", "wait_start": now - timedelta(minutes=2)}
    p_warn = {"nivel_triaje": "Nivel I", "wait_start": now - timedelta(minutes=6)}
    p_crit = {"nivel_triaje": "Nivel I", "wait_start": now - timedelta(minutes=12)}
    
    assert get_wait_time_alert(p_normal) == "normal"
    assert get_wait_time_alert(p_warn) == "warning"
    assert get_wait_time_alert(p_crit) == "critical"
