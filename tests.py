# -*- encoding: utf-8 -*-

"""
Copyright (c) 2019 - present applicationSeed.us
"""

import pytest
import json

from api import application

"""
   Sample test data
"""

DUMMY_USERNAME = "applicationle"
DUMMY_EMAIL = "applicationle@applicationle.com"
DUMMY_PASS = "newpassword"


DUMMY_MOOD_TITLE = 'sad'
DUMMY_MOOD_VALUE = 1
DUMMY_MOOD_NOTES = 'lorem ipsum' 

@pytest.fixture
def client():
    with application.test_client() as client:
        yield client

def test_user_signup(client):
    """
       Tests /users/register API
    """
    response = client.post(
        "api/users/register",
        data=json.dumps(
            {
                "username": DUMMY_USERNAME,
                "email": DUMMY_EMAIL,
                "password": DUMMY_PASS
            }
        ),
        content_type="applicationlication/json")

    data = json.loads(response.data.decode())
    assert response.status_code == 200
    assert "The user was successfully registered" in data["msg"]


def test_user_signup_invalid_data(client):
    """
       Tests /users/register API: invalid data like email field empty
    """
    response = client.post(
        "api/users/register",
        data=json.dumps(
            {
                "username": DUMMY_USERNAME,
                "email": "",
                "password": DUMMY_PASS
            }
        ),
        content_type="applicationlication/json")

    data = json.loads(response.data.decode())
    assert response.status_code == 400
    assert "'' is too short" in data["msg"]


def test_user_login_correct(client):
    """
       Tests /users/signup API: Correct credentials
    """
    response = client.post(
        "api/users/login",
        data=json.dumps(
            {
                "email": DUMMY_EMAIL,
                "password": DUMMY_PASS
            }
        ),
        content_type="applicationlication/json")

    data = json.loads(response.data.decode())
    assert response.status_code == 200
    assert data["token"] != ""


def test_user_login_error(client):
    """
       Tests /users/signup API: Wrong credentials
    """
    response = client.post(
        "api/users/login",
        data=json.dumps(
            {
                "email": DUMMY_EMAIL,
                "password": DUMMY_EMAIL
            }
        ),
        content_type="applicationlication/json")

    data = json.loads(response.data.decode())
    assert response.status_code == 400
    assert "Wrong credentials." in data["msg"]

def test_valid_mood_insert(client):
    """
        Tests /moods API
    """
    response = client.post(
        "api/moods",
        data=json.dumps(
            {
                'title': DUMMY_MOOD_TITLE,
                'value': DUMMY_MOOD_VALUE,
                'notes': DUMMY_MOOD_NOTES
            }
        ),
        content_type="applicationlication/json")

    data = json.loads(response.data.decode())
    assert response.status_code == 400
    assert "Something went wrong" in data["msg"]

