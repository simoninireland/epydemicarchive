# Forms
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

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.widgets import TextArea


class EditProfile(FlaskForm):

    name = StringField('Name (optional)')
    affiliation = StringField('University or affiliation (optional)')
    url = StringField('Home page (optional)')
    bio = TextAreaField('Biography (optional)', widget=TextArea())
    submit = SubmitField('Update')
    cancel = SubmitField('Cancel')
    api_key = SubmitField('Generate a new API key')
