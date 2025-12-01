import pytest
from unittest.mock import MagicMock, patch
from bson import ObjectId
from services.notification_service import (
    create_notification, 
    _send_email, 
    _send_webhook,
    NotificationChannel,
    NotificationPriority,
    NotificationCategory
)

@pytest.fixture
def mock_db_notifications(mock_db):
    return mock_db.notifications

@pytest.fixture(autouse=True)
def patch_notification_service_db(mock_db):
    with patch('services.notification_service.get_database', return_value=mock_db):
        yield

def test_create_notification_in_app_only(mock_db_notifications):
    notif_id = create_notification(
        title="Test",
        message="Hello",
        channels=[NotificationChannel.IN_APP]
    )
    
    assert notif_id is not None
    
    # Verify document structure
    # Try finding by title to avoid ObjectId/String mismatch issues in mongomock if any
    doc = mock_db_notifications.find_one({"title": "Test"})
    assert doc is not None
    assert str(doc["_id"]) == notif_id
    assert doc["channels"] == ["in_app"]

@patch('services.notification_service._send_email')
def test_create_notification_with_email(mock_send_email, mock_db_notifications):
    mock_send_email.return_value = True
    
    create_notification(
        title="Email Test",
        message="Body",
        channels=[NotificationChannel.EMAIL]
    )
    
    mock_send_email.assert_called_once()

@patch('smtplib.SMTP')
@patch('db.repositories.notification_config.get_smtp_config')
def test_send_email_success(mock_get_config, mock_smtp):
    mock_get_config.return_value = {
        "enabled": True,
        "host": "smtp.test.com",
        "port": 587,
        "username": "user",
        "password": "pass",
        "from_email": "test@test.com"
    }
    
    notification = {
        "title": "Test Subject",
        "message": "Test Message Body",  # Added message field
        "recipients": ["admin"],
        "category": "general",
        "priority": "medium"
    }
    
    # Patching where it is defined, assuming it is imported in notification_service
    # If notification_service does 'from templates.email_templates import get_recipient_emails'
    # we should patch 'templates.email_templates.get_recipient_emails' (since src is in path)
    with patch('templates.email_templates.get_recipient_emails', return_value=["admin@test.com"]):
        success = _send_email(notification)
        assert success == True
        mock_smtp.return_value.send_message.assert_called_once()

@patch('requests.post')
@patch('db.repositories.notification_config.get_webhook_config')
def test_send_webhook_success(mock_get_config, mock_post):
    mock_get_config.return_value = {
        "enabled": True,
        "url": "http://webhook.com",
        "type": "slack"
    }
    mock_post.return_value.status_code = 200
    
    notification = {
        "title": "Webhook Test",
        "message": "Alert",
        "priority": "high"
    }
    
    success = _send_webhook(notification)
    assert success == True
    mock_post.assert_called_once()
