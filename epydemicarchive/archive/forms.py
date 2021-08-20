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
from wtforms import Field, StringField, TextAreaField, SubmitField, SelectMultipleField, FormField, FieldList
from flask_wtf.file import FileField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError
from wtforms.widgets import TextInput, TextArea
from epydemicarchive.archive.models import Network


class TagField(Field):
    '''A field that allows tags to be entered as a comma-seperated
    text list. The list is then decomposed into tags which are
    normalised to lower case.'''
    widget = TextInput()

    def _value(self):
        '''Turn the list of tags into a string for the form.'''
        if self.data:
            return ', '.join(self.data)
        else:
            return ''

    def process_formdata(self, valuelist):
        '''Turn the comma-separated field value into a list of tags.

        :param valuelist: list of field values (only one)'''
        if valuelist:
            self.data = self._remove_duplicates([x.strip() for x in valuelist[0].split(',')])
        else:
            self.data = []

    def _remove_duplicates(self, tags):
        '''Remove any duplicate tags. The tag order is preserved, but
        all tags are made lowercase. Also remove empty tags.

        :param tags: the list of tags
        :returns: a list of tags with duplicates removed'''
        newtags = []
        for t in tags:
            if len(t) > 0:
                tl = t.lower()
                if tl not in newtags:
                    newtags.append(tl)
        return newtags


class UploadNetwork(FlaskForm):

    file = FileField('Network filename')
    title = StringField('Title (optional)')
    description = TextAreaField('Description (optional)', widget=TextArea())
    tags = TagField('Tags')
    submit = SubmitField('Upload')

    def validate_file(self, field):
        '''Validate that the network filename has one of the expected extensions.

        :param field: the field'''
        filename = field.data.filename
        if Network.is_acceptable_file(filename) is None:
            raise ValidationError(f'File {filename} does not have a recognised extension')


class EditNetwork(FlaskForm):

    title = StringField('Title (optional)')
    description = TextAreaField('Description (optional)', widget=TextArea())
    tags = TagField('Tags')
    submit = SubmitField('Update')
    cancel = SubmitField('Cancel')
    download = SubmitField('Download network')
    delete = SubmitField("Delete network")


class SearchNetworks(FlaskForm):

    tags = TagField('Tags')
    metadata = StringField('Metadata')
    add_tag = StringField('New tag')
    add_meta_key = StringField('New key')
    add_meta_value = StringField('New value')
    refine = SubmitField('Refine selection')
    reset = SubmitField("Reset selection")
