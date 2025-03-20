import os
import pytest
import tempfile
from app import app
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    """Fixture to create a Flask test client"""
    app.config['TESTING'] = True
    client = app.test_client()
    yield client

@patch('app.api.media_upload')
@patch('app.api.update_status')
def test_create_post(mock_update_status, mock_media_upload, client):
    """Test the /create endpoint"""
    
    # Mock the media upload response
    mock_media_upload.return_value = MagicMock(media_id='12345')

    # Mock the tweet creation response
    mock_update_status.return_value = MagicMock(id_str='67890')

    # Create a temporary image file
    with tempfile.NamedTemporaryFile(suffix=".jpg") as temp_image:
        temp_image.write(b'test data')
        temp_image.seek(0)
        
        # Send a POST request to the /create endpoint
        response = client.post(
            '/create',
            data={'text': 'Test tweet'},
            content_type='multipart/form-data',
            files={'file': (temp_image.name, temp_image, 'image/jpeg')}
        )
    
    # Validate response
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "Tweet posted successfully"
    assert json_data['tweet_id'] == '67890'
    
    # Ensure mock methods were called
    mock_media_upload.assert_called_once()
    mock_update_status.assert_called_once_with(status="Test tweet", media_ids=['12345'])
