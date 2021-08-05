# User profile model
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

from epydemicarchive import db


class Profile(db.Model):
    '''User profile model. This includes metadata about the user, all
    voluntary. The required parts of the user data (essentially
    everything needed to do authentication) are stored in the User
    model.
    '''

    user_id = db.Column(db.String(128), db.ForeignKey('user.id'),
                        nullable=False, primary_key=True)
    user = db.relationship('User', backref=db.backref('profile', lazy=True))

    name = db.Column(db.String(128))
    affiliation = db.Column(db.String(128))
    url = db.Column(db.String(128))
    bio = db.Column(db.String(2048))

    @staticmethod
    def from_user(u):
        '''Return the profile of the given user. A blamnk profile is
        created if none exists.

        :param u: the user
        :returns: the user's profile.'''
        p = Profile.query.filter_by(user=u).first()
        if p is None:
            p = Profile.create_profile(u)
        return p

    @staticmethod
    def create_profile(u):
        '''Create a blank profile for the given user.

        :param u: the user
        :returns: the profile'''
        p = Profile(user=u,
                    name='',
                    affiliation='',
                    url = '',
                    bio = '')
        db.session.add(p)
        return p
