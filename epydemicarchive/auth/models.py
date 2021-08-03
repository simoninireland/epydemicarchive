# User model
#
# Copyright (C) 2021 Simon Dobson
#
# This file is part of epydemicarchive, a server for complex network archives.
#
# epydemicerchive is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# epydemicarchive is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with epydemicarchive. If not, see <http://www.gnu.org/licenses/gpl.html>.

import os
import base64
from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from epydemicarchive import db, login


@login.user_loader
def load_user(id):
    '''Return the user associated with the given unique internal
    is, used for logging in.

    :param id: the user id
    :returns: the user object'''
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    '''User model. This includes basic identification and authentication
    information for both interactive (web) and programmatic (API) access.

    New users are automatically allocated an API key valid for a year.
    '''

    # Basic information
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    # API access
    api_key = db.Column(db.String(128))
    api_key_expires= db.Column(db.DateTime)


    # ---------- Password assignment and checking ----------

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    # ---------- API key assignment and checking ----------

    def get_api_key(self, expires_in=60 * 24 * 265):
        '''Return the API key of the user, creating one that expires
        after the given number of seconds if none exists.

        :param expires_in: the time in seconds for the API key to be validate
        :returns: the key'''
        now = datetime.utcnow()
        if not self.api_key or self.api_key_expires > now + timedelta(seconds=60):
            # create a new API key
            self.api_key = base64.b64encode(os.urandom(24)).decode('utf-8')
            self.api_key_expires = now + timedelta(seconds=expires_in)
            db.session.add(self)
        return self.api_key

    def check_api_key(self, token):
        '''Check whether the given token is a valid API key for this user. To be
        valid the token must match and not have expired.

        :param token: the token presented by the client
        :returns: True if the token is valid'''
        now = datetime.utcnow()
        if self.api_key is None:
            return False
        if self.api_key != token:
            return False
        if self.api_key_expires < now:
            self.revoke_api_key()    # now we know it's expired
            return False
        return True

    def revoke_api_key(self):
        '''Revoke the API key for this user.'''
        self.api_key = None


    # ---------- Static helper methods ----------

    @staticmethod
    def from_email(email):
        '''Retrieve the user with the given email address.

        :param email: the email address
        :returns: the user or None'''
        return User.query.filter_by(email=email).first()

    @staticmethod
    def from_api_key(token):
        '''Retrieve a user by their API key. The key must not have expired.

        :param token: the token presented by the client
        :returns: the user or None'''
        now = datetime.utcnow()
        u = User.query.filter_by(api_key=token).first()
        if u is None:
            return None
        if u.api_key_expires < now:
            u.revoke_api_key()    # now we know it's expired
            return None
        return u

    @staticmethod
    def exists(email):
        '''Check whether the given user exists.

        :param: the email address
        :returns: True if the user is known'''
        return User.query.filter_by(email=email).first() is not None

    @staticmethod
    def create_user(email, password):
        '''Create a new user.

        :param email: the user's email address
        :param password: the password
        :returns: the email address'''
        u = User(email=email)
        u.set_password(password)
        u.get_api_key()
        db.session.add(u)

        return email
