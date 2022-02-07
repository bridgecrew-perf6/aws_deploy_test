import json
import pytest
import config
import bcrypt

from sqlalchemy import create_engine, text
from app import create_app

database = create_engine(config.test_config['DB_URL'], encoding='utf-8', max_overflow=0)

@pytest.fixture
def api():
    app = create_app(config.test_config)
    app.config['TEST'] = True
    api = app.test_client()
    return api

def setup_function():
    hashed_password = bcrypt.hashpw(
        b"test_password",
        bcrypt.gensalt()
    )
    new_users = [{
        'id': 1,
        'email': 'test@gmail.com',
        'password': hashed_password,
        'name': 'test_kim',
        'profile': 'test profile'
    }, {
        'id': 2,
        'email': 'test@naver.com',
        'password': hashed_password,
        'name': 'test_lee',
        'profile': 'test_2'
    }]
    database.execute(text("""
        INSERT INTO users (
            name,
            email,
            profile,
            hashed_password
        ) VALUES (
            :name,
            :email,
            :profile,
            :password
        )
    """), new_users)

    database.execute(text("""
        INSERT INTO tweets (
            user_id,
            tweet
        ) VALUES (
            2,
            "hello world~"
        )
    """))

def teardown_function():
    database.execute(text("""SET FOREIGN_KEY_CHECKS=0"""))
    database.execute(text("""TRUNCATE users"""))
    database.execute(text("""TRUNCATE tweets"""))
    database.execute(text("""TRUNCATE users_follow_list"""))
    database.execute(text("""SET FOREIGN_KEY_CHECKS=1"""))

def test_ping(api):
    resp = api.get('/ping')
    assert b'pong' in resp.data

def test_login(api):
    resp = api.post(
        '/login',
        data = json.dumps({'email': "test@gmail.com", 'password': "test_password"}),
        content_type = 'application/json'
    )
    assert b"access_token" in resp.data

def test_authorized(api):
    resp = api.post(
        '/tweet',
        data = json.dumps({'tweet': "hello world!"}),
        content_type = 'application/json'
    )
    assert resp.status_code == 401 # no token

    resp = api.post(
        '/follow',
        data = json.dumps({'follow': 2}),
        content_type = 'application/json'
    )
    assert resp.status_code == 401 # no token

    resp = api.post(
        '/unfollow',
        data = json.dumps({'unfollow': 2}),
        content_type = 'application/json'
    )
    assert resp.status_code == 401 # no token

def test_tweet(api):
    # login, tweet
    resp = api.post(
        '/login',
        data = json.dumps({'email': 'test@gmail.com', 'password': 'test_password'}),
        content_type = 'application/json'
    )
    resp_json = json.loads(resp.data.decode('utf-8'))
    access_token = resp_json['access_token']

    resp = api.post(
        '/tweet',
        data = json.dumps({'tweet': 'hello world!'}),
        content_type = 'application/json',
        headers = {'Authorization': access_token}
    )
    assert resp.status_code == 200
    # timeline
    resp = api.get(f'/timeline/1')
    tweets = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == 200
    assert tweets == {
        'user_id': 1,
        'timeline': [
            {
                'user_id': 1,
                'tweet': "hello world!"
            }
        ]
    }

def test_follow(api):
    resp = api.post(
        '/login',
        data=json.dumps({'email': 'test@gmail.com', 'password': 'test_password'}),
        content_type='application/json'
    )
    resp_json = json.loads(resp.data.decode('utf-8'))
    access_token = resp_json['access_token']

    resp = api.get('/timeline/1')
    tweets = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == 200
    assert tweets == {
        'user_id': 1,
        'timeline': []
    }

    resp = api.post(
        '/follow',
        data = json.dumps({'follow': 2}),
        content_type = 'application/json',
        headers = {'Authorization': access_token}
    )
    assert resp.status_code == 200

    resp = api.get('timeline/1')
    tweets = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == 200
    assert tweets == {
        'user_id': 1,
        'timeline': [
            {
                'user_id': 2,
                'tweet': "hello world~"
            }
        ]
    }

def test_unfollow(api):
    resp = api.post(
        '/login',
        data=json.dumps({'email': 'test@gmail.com', 'password': 'test_password'}),
        content_type='application/json'
    )
    resp_json = json.loads(resp.data.decode('utf-8'))
    access_token = resp_json['access_token']

    resp = api.post(
        '/follow',
        data=json.dumps({'follow': 2}),
        content_type='application/json',
        headers={'Authorization': access_token}
    )
    assert resp.status_code == 200

    resp = api.get('timeline/1')
    tweets = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == 200
    assert tweets == {
        'user_id': 1,
        'timeline': [
            {
                'user_id': 2,
                'tweet': "hello world~"
            }
        ]
    }

    resp = api.post(
        '/unfollow',
        data = json.dumps({'unfollow': 2}),
        content_type = 'application/json',
        headers = {'Authorization': access_token}
    )
    assert resp.status_code == 200

    resp = api.get('/timeline/1')
    tweets = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == 200
    assert tweets == {
        'user_id': 1,
        'timeline': []
    }