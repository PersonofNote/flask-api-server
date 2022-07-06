# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from datetime import datetime, timezone, timedelta

from functools import wraps

from flask import request
from flask_restx import Api, Resource, fields

import jwt

import models 
#import db, Users, Moods, JWTTokenBlocklist
import config

import json

from flask_restx import reqparse

parser = reqparse.RequestParser()
parser.add_argument("userID", type=int)


rest_api = Api(version="1.0", title="Users API")


"""
    Flask-Restx models for api request and response data
"""

signup_model = rest_api.model('SignUpModel', {"username": fields.String(required=True, min_length=2, max_length=32),
                                              "email": fields.String(required=True, min_length=4, max_length=64),
                                              "password": fields.String(required=True, min_length=4, max_length=16)
                                              })

login_model = rest_api.model('LoginModel', {"email": fields.String(required=True, min_length=4, max_length=64),
                                            "password": fields.String(required=True, min_length=4, max_length=16)
                                            })

user_edit_model = rest_api.model('UserEditModel', {"userID": fields.String(required=True, min_length=1, max_length=32),
                                                   "username": fields.String(required=True, min_length=2, max_length=32),
                                                   "email": fields.String(required=True, min_length=4, max_length=64),
                                                   "role": fields.String(required=False, min_length=3, max_length=12)
                                                   })

user_delete_model = rest_api.model('UserDeleteModel', {
                                                "userID": fields.String(required=True, min_length=1, max_length=32),
                                            })

mood_fetch_model = rest_api.model('MoodFetchModel', {"userId": fields.String(required=True, min_length=1, max_length=32)
                                            })

mood_input_model = rest_api.model('MoodInputModel', {"title": fields.String(required=True, min_length=4, max_length=12),
                                            "value": fields.Integer(required=True, min=0, max=5),
                                            "notes": fields.String(required=False, min_length=0, max_length=500)
                                            })
# CHECK IF THIS REQUIRES TOO MANY THINGS. You might just need the id to delete                                            
mood_delete_model = rest_api.model('MoodDeleteModel', {
                                            "moodID": fields.String(required=True, min_length=1, max_length=32),
                                            })


"""
   Helper function for JWT token required
"""

def token_required(f):

    @wraps(f)
    def decorator(*args, **kwargs):

        token = None

        if "authorization" in request.headers:
            token = request.headers["authorization"]

        if not token:
            return {"success": False, "msg": "Valid JWT token is missing"}, 400

        try:
            data = jwt.decode(token, config.BaseConfig.SECRET_KEY, algorithms=["HS256"])
            current_user = models.Users.get_by_email(data["email"])

            if not current_user:
                return {"success": False,
                        "msg": "Sorry. Wrong auth token. This user does not exist."}, 400

            token_expired = models.db.session.query(JWTTokenBlocklist.id).filter_by(jwt_token=token).scalar()

            if token_expired is not None:
                return {"success": False, "msg": "Token revoked."}, 400

            if not current_user.check_jwt_auth_active():
                return {"success": False, "msg": "Token expired."}, 400

        except:
            return {"success": False, "msg": "Token is invalid"}, 400

        return f(current_user, *args, **kwargs)

    return decorator


"""
    Flask-Restx routes
"""


@rest_api.route('/api/users/register')
class Register(Resource):
    """
       Creates a new user by taking 'signup_model' input
    """

    @rest_api.expect(signup_model, validate=True)
    def post(self):

        req_data = request.get_json()

        _username = req_data.get("username")
        _email = req_data.get("email")
        _password = req_data.get("password")

        user_exists = models.Users.get_by_email(_email)
        if user_exists:
            return {"success": False,
                    "msg": "Email already taken"}, 400

        new_user = models.Users(username=_username, email=_email)

        new_user.set_password(_password)
        new_user.save()
        return {"success": True,
                "userID": new_user.id,
                "msg": "The user was successfully registered"}, 200

@rest_api.route('/api/users')
class UserUtilities(Resource):
    """
        Gets a list of all users for admin purposes
    """
    @token_required
    def get(self):
        a = models.Users.query.all()
        user_json = [s.toJSON() for s in a]
        return {"success": True, "userList": json.dumps(user_json)}, 200

@rest_api.route('/api/users/delete')
class UserDelete(Resource):
    """
        Deletes a user
    """

    @rest_api.expect(user_delete_model, validate=True)
    def delete(self):
        # TODO: update to iterate of a list for batch deletion
        req_data = request.get_json()

        _userid = req_data.get("id")
        users = models.Users.get_by_id(_userid)
        users.delete(users)
        return {"success": True, "deletedUser": "Deleted"}, 200

@rest_api.route('/api/users/login')
class Login(Resource):
    """
       Login user by taking 'login_model' input and return JWT token
    """

    @rest_api.expect(login_model, validate=True)
    def post(self):

        req_data = request.get_json()

        _email = req_data.get("email")
        _password = req_data.get("password")

        user_exists = models.Users.get_by_email(_email)

        if not user_exists:
            return {"success": False,
                    "msg": "This email does not exist."}, 400

        if not user_exists.check_password(_password):
            return {"success": False,
                    "msg": "Wrong credentials."}, 400
        

        # create access token uwing JWT
        token = jwt.encode({'email': _email, 'exp': datetime.utcnow() + timedelta(minutes=30)}, config.BaseConfig.SECRET_KEY)

        user_exists.set_jwt_auth_active(True)
        user_exists.save()
        user_data = user_exists.toJSON()
        # Convert ['moods'] to json
        user_data['moods'] = [m.toJSON() for m in user_data['moods']]

        return {"success": True,
                "token": token,
                "user": user_data}, 200


@rest_api.route('/api/users/edit')
class EditUser(Resource):
    """
       Edits User's username or password or both using 'user_edit_model' input
    """

    @rest_api.expect(user_edit_model)
    @token_required
    def post(self, current_user):

        req_data = request.get_json()

        _new_username = req_data.get("username")
        _new_email = req_data.get("email")
        _new_role = req_data.get("role")

        if _new_username:
            self.update_username(_new_username)

        if _new_email:
            self.update_email(_new_email)
        
        if _new_role:
            self.update_role(_new_role)

        self.save()

        return {"success": True}, 200


@rest_api.route('/api/users/logout')
class LogoutUser(Resource):
    """
       Logs out User using 'logout_model' input
    """

    @token_required
    def post(self, current_user):

        _jwt_token = request.headers["authorization"]

        jwt_block = models.JWTTokenBlocklist(jwt_token=_jwt_token, created_at=datetime.now(timezone.utc))
        jwt_block.save()

        self.set_jwt_auth_active(False)
        self.save()

        return {"success": True}, 200

@rest_api.route('/api/users/<int:user_id>')
class GetMoods(Resource):
    """
       Gets all moods for a user
    """
    def get(self, user_id):
        try:
            m = models.Moods.get_all_for_user(user_id)
            mood_json = [s.toJSON() for s in m]

            return {"success": True,
                    "moods": mood_json,
                    "msg": "All moods for user"}, 200
        except:
            return {"success": False,
                "moods": [],
                "msg": "Error fetching mood data for user"
            }, 400


@rest_api.route('/api/moods/input')
class AddMood(Resource):
    """
       Creates a new mood entry by taking 'mood' input
    """

    @rest_api.expect(mood_input_model, validate=True)
    def post(self):

        req_data = request.get_json()

        _title = req_data.get("title")
        _value = req_data.get("value")
        _notes = req_data.get("notes")
        _userID = req_data.get("userID")

        new_mood = models.Moods(title=_title, value=_value, notes=_notes, user_id=_userID)
        new_mood.save()

        # Pass the mood data back to the client to add it to the list without refreshing the page
        new_mood_data = new_mood.toJSON()
        res = {"success": True,
                "mood_data": new_mood_data,
                "msg": "Added new mood entry"}
        print(res)
        return res, 200

@rest_api.route('/api/moods/delete')
class DeleteMood(Resource):
    """
       Deletes one mood entry
    """

    @rest_api.expect(mood_delete_model, validate=True)
    def delete(self):

        req_data = request.get_json()

        _id = req_data.get("moodID")

        mood_to_del = models.Moods.get_by_id(id=_id)
        mood_to_del.delete(mood_to_del)

        # TODO: return moods back to the user... 
        return {"success": True,
                "moodID": mood_to_del.id,
                "msg": "Removed mood entry"}, 200