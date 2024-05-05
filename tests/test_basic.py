import pytest
from unittest.mock import patch
from tele import Teleboy


@pytest.fixture
def teleboy_instance():
    token = "your_token"
    return Teleboy(token)


@patch("tele.Teleboy._get")
def test_get_chats_success(mock_get, teleboy_instance):
    mock_get.return_value = {
        "result": [
            {"message": {"chat": {"id": 123, "title": "Test Group", "type": "group"}}}
        ],
        "ok": True,
    }
    chats = teleboy_instance.get_chats()
    assert chats == {123: "Test Group"}


@patch("tele.Teleboy._get")
def test_get_chats_error(mock_get, teleboy_instance):
    mock_get.return_value = {"error": 404}
    chats = teleboy_instance.get_chats()
    assert not chats
    mock_get.return_value = {"ok": False}
    chats = teleboy_instance.get_chats()
    assert not chats


@patch("tele.Teleboy._get")
def test_send_msg_success(mock_get, teleboy_instance):
    chat_id = "123"
    text = "Test message"
    mock_get.return_value = {"status": "sent"}
    teleboy_instance.send_msg(chat_id, text)


@patch("tele.Teleboy._get")
def test_send_msg_long_text(mock_get, teleboy_instance):
    chat_id = "123"
    text = (
        "A very long test message that needs to"
        "be chunked into smaller parts because it exceeds the chunk size."
    )
    mock_get.return_value = {"status": "sent"}
    teleboy_instance.chunk_size = 30
    teleboy_instance.send_msg(chat_id, text)


@patch("tele.Teleboy._get")
def test_get_chats_wrong_token(mock_get, teleboy_instance):
    mock_get.return_value = {"error": 404}
    chats = teleboy_instance.get_chats()
    assert chats == {}
