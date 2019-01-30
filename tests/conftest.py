import os
import tempfile

import pytest
from moviefriday import create_app
from moviefriday.db import get_db


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'MONGO_DB': 'flixdb_test'
    })

    with app.app_context():
        dbConfig = get_db()
        dbConfig.flix_db.drop_collection('users')
        dbConfig.flix_db.drop_collection('users')

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
