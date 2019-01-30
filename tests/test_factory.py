from moviefriday import create_app


def test_config():
    assert create_app({'TESTING': True}).testing


def test_minimal_health_endpoint_present(client):
    response = client.get('/health')
    assert response.data == b'All good!'
