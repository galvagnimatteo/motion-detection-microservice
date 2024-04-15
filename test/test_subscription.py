from unittest.mock import MagicMock, patch

import cv2
import numpy as np

from src.model.dtos.input.SubscriptionInputDto import SubscriptionInputDto


def test_given_working_camera_create_subscription_should_return_ok(client):
    mock_capture = MagicMock(spec=cv2.VideoCapture)
    mock_capture.isOpened.return_value = True
    mock_capture.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))

    with patch("cv2.VideoCapture", return_value=mock_capture):
        input_data = SubscriptionInputDto(
            camera_url="https://example.com/camera",
            movement_callback_url="https://example.com/movement",
            crash_callback_url="https://example.com/crash",
            min_contour_area=100,
            cooldown_seconds=30
        )

        response = client.post("/", json=input_data.dict())

        assert response.status_code == 200


def test_given_not_working_camera_create_subscription_should_return_bad_request(client):
    mock_capture = MagicMock(spec=cv2.VideoCapture)
    mock_capture.isOpened.return_value = False

    with patch("cv2.VideoCapture", return_value=mock_capture):
        input_data = SubscriptionInputDto(
            camera_url="https://example.com/camera",
            movement_callback_url="https://example.com/movement",
            crash_callback_url="https://example.com/crash",
            min_contour_area=100,
            cooldown_seconds=30
        )

        response = client.post("/", json=input_data.dict())

        assert response.status_code == 400


def test_given_already_existent_subscription_create_subscription_should_return_bad_request(client):
    mock_capture = MagicMock(spec=cv2.VideoCapture)
    mock_capture.isOpened.return_value = True
    mock_capture.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))

    with patch("cv2.VideoCapture", return_value=mock_capture):
        input_data = SubscriptionInputDto(
            camera_url="https://example.com/camera",
            movement_callback_url="https://example.com/movement",
            crash_callback_url="https://example.com/crash",
            min_contour_area=100,
            cooldown_seconds=30
        )

        firstResponse = client.post("/", json=input_data.dict())
        response = client.post("/", json=input_data.dict())

        assert firstResponse.status_code == 200
        assert response.status_code == 400


def test_given_non_existent_subscription_get_subscription_should_return_not_found(client):
    mock_capture = MagicMock(spec=cv2.VideoCapture)
    mock_capture.isOpened.return_value = True
    mock_capture.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))

    with patch("cv2.VideoCapture", return_value=mock_capture):
        input_data = SubscriptionInputDto(
            camera_url="https://example.com/camera",
            movement_callback_url="https://example.com/movement",
            crash_callback_url="https://example.com/crash",
            min_contour_area=100,
            cooldown_seconds=30
        )

        firstResponse = client.post("/", json=input_data.dict())
        response = client.get("/?camera_url=https://example.com/camera")

        assert firstResponse.status_code == 200
        assert response.status_code == 200


def test_given_already_existent_subscription_get_subscription_should_return_ok(client):
    response = client.get("/?camera_url=https://example.com/camera")

    assert response.status_code == 404


def test_given_already_existent_subscription_delete_subscription_should_return_no_content(client):
    mock_capture = MagicMock(spec=cv2.VideoCapture)
    mock_capture.isOpened.return_value = True
    mock_capture.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))

    with patch("cv2.VideoCapture", return_value=mock_capture):
        input_data = SubscriptionInputDto(
            camera_url="https://example.com/camera",
            movement_callback_url="https://example.com/movement",
            crash_callback_url="https://example.com/crash",
            min_contour_area=100,
            cooldown_seconds=30
        )

        firstResponse = client.post("/", json=input_data.dict())
        response = client.delete("/?camera_url=https://example.com/camera")

        assert firstResponse.status_code == 200
        assert response.status_code == 204


def test_given_not_existent_subscription_delete_subscription_should_return_not_found(client):
    response = client.delete("/?camera_url=https://example.com/camera")

    assert response.status_code == 404
