# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from datetime import datetime

import json

from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Users(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.Text())
    date_joined = db.Column(db.DateTime(), default=datetime.utcnow)
    role = db.Column(db.String(32), default="user")
    premium = db.Column(db.Boolean(), default=False)
    premium_start_date = db.Column(db.DateTime(), nullable=True)
    premium_start_date = db.Column(db.DateTime(), nullable=True)
    children = db.relationship("Moods")

    jwt_auth_active = db.Column(db.Boolean())

    def __repr__(self):
        return f"User {self.username}"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def update_email(self, new_email):
        self.email = new_email

    def update_username(self, new_username):
        self.username = new_username

    def update_role(self, new_role):
        self.role = new_role

    def update_premium(self, is_premium):
        self.premium = is_premium

    def check_jwt_auth_active(self):
        return self.jwt_auth_active

    def set_jwt_auth_active(self, set_status):
        self.jwt_auth_active = set_status

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def toDICT(self):

        cls_dict = {}
        cls_dict['_id'] = self.id
        cls_dict['username'] = self.username
        cls_dict['email'] = self.email
        cls_dict['role'] = self.role
        cls_dict['moods'] = self.children

        return cls_dict

    def toJSON(self):

        return self.toDICT()
    
    def delete(cls, user):
        db.session.delete(user)
        db.session.commit()

class Moods(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(32), nullable=False)
    value = db.Column(db.SmallInteger(), nullable=False)
    creation_time = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    notes = db.Column(db.String(500), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __repr__(self):
        return f"Mood {self.title}"

    def save(self):
        db.session.add(self)
        db.session.commit()


    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).all()

    @classmethod
    def get_by_value(cls, value):
        return cls.query.filter_by(value=value).all()

    @classmethod
    def get_all_for_user(cls, value):
        return cls.query.filter_by(user_id=value).all()

    def toDICT(self):

        cls_dict = {}
        cls_dict['_id'] = self.id
        cls_dict['title'] = self.title
        cls_dict['value'] = self.value
        cls_dict['notes'] = self.notes
        cls_dict['created_at'] = json.dumps(self.creation_time, default=str)

        return cls_dict

    def toJSON(self):

        return self.toDICT()

    def delete(cls, id):
        db.session.delete(id)
        db.session.commit()


class JWTTokenBlocklist(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    jwt_token = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=True) 

    def __repr__(self):
        return f"Expired Token: {self.jwt_token}"

    def save(self):
        db.session.add(self)
        db.session.commit()
