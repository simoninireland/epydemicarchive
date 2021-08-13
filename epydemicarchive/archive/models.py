# Archive data model
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
import re
import uuid
from datetime import datetime
import networkx
from flask import current_app
from epydemicarchive import db


tags = db.Table('tags',
                db.Column('network', db.ForeignKey('network.id'), primary_key=True),
                db.Column('tag', db.ForeignKey('tag.id'), primary_key=True))


class Network(db.Model):
    '''Network data model. This records the metadata about a network held
    in the archive.
    '''

    # The file types of networks we recognise, with their names
    # and fuloader functions
    FILETYPES = {
        'al': ('adjacency list', networkx.read_adjlist),
    }

    # The file types of compressions we recognise
    COMPRESSIONS = [ 'gz', 'bz2']

    # The regexp for all the acceptable extensions for network files
    # sd: should be constructed from the above
    NetworkFileExtensions = re.compile(r'.+?\.(al.gz)$')

    # The regexp to extract the file's type (extension)
    # sd: should be constructed from the above
    NetworkFileType = re.compile(r'.+?\.([a-zA-Z0-9]+)(\.((gz)|(bz2)))?$')

    # Location information
    id = db.Column(db.String(64), primary_key=True)
    filename = db.Column(db.String(256))             # relative to ARCHIVE_DIR

    # Lifecycle
    uploaded = db.Column(db.DateTime)
    available = db.Column(db.Boolean)

    # Metadata
    title = db.Column(db.String(256))
    description = db.Column(db.String(1024))
    tags = db.relationship('Tag', secondary=tags, lazy='subquery',
                           backref=db.backref('networks', lazy=True))
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', backref=db.backref('networks', lazy=True))


    def tagnames(self):
        '''Return a list of tag names.

        :returns: the network's tags'''
        return [tag.name for tag in self.tags]

    def network_filename(self):
        '''Return the file in the archive holding the network.

        :returns: the filename'''
        return os.path.join(current_app.config['ARCHIVE_DIR'],
                            self.filename)

    def load_network(self):
        '''Load the network into memory using networkx. This involves
        working out the type of network representation uploaded.

        :returns: the raw network'''
        filename = self.network_filename()

        # extract the file type from the filename
        m = Network.NetworkFileType.match(filename)
        if m is None:
            raise Exception('Can\'t determine network type')
        t = m[1]

        # read network
        if t in self.FILETYPES:
            # use the loader function to load the network
            (_, loader) = self.FILETYPES[t]
            g = loader(filename)
        else:
            # unknown type
            raise Exception(f'Unknown network file type {t}')

        return g

    def get(self, key, default=None):
        '''Return the given metadata element. The default is returned
        if the element is not present.

        :param key: the key
        :param default: the default value
        :returns: the associated value or the default value'''
        meta = Metadata.query.filter_by(network=self, key=key).first()
        return meta.value if meta else default

    def __getitem__(self, key):
        '''Dict-based interface for accessing metadata. Uses :meth:`get`.

        :param key: the key
        :returns: the associated value'''
        return self.get(key)


    # ---------- Static helper methods ----------

    @staticmethod
    def from_uuid(id):
        '''Return the network with the given UUID.

        :param id: the UUId
        :returns: the network or None'''
        return Network.query.filter_by(id=id).first()

    @staticmethod
    def is_acceptable_file(filename):
        '''Test whether the given filename has an acceptable extension.
        This is a sub-set of the file types handled by NetworkX.

        :param filename: the filename
        :returns: the network model's acceptable extension, or None'''
        m = Network.NetworkFileExtensions.match(filename)
        return None if m is None else m[1]

    @staticmethod
    def create_network(user, filename, data, title, desc, tags):
        '''Create a new network object.

        :param user: the owner of the network
        :param filename: the filename of the uploaded network
        :param data: the uploaded network data stream
        :param title: the network title
        :param desc: the network description
        :param tags: a list of tags for the network
        :returns: the network'''

        # create a UUID for this new network
        id = str(uuid.uuid4())

        # construct a filename for the uploaded network, maintaining
        # the original extension
        ext = Network.is_acceptable_file(filename)
        basename = f'{id}.{ext}'
        full = os.path.join(current_app.config['ARCHIVE_DIR'],
                            basename)

        # save the uploaded network into the archive directory
        data.save(full)

        # create the network
        now = datetime.utcnow()
        n = Network(id=id,
                    filename=basename,
                    owner=user,
                    uploaded=now,
                    available=False,
                    title=title,
                    description=desc,
                    tags=Tag.ensure_tags(tags))
        db.session.add(n)

        return n

    @staticmethod
    def delete_network(n):
        '''Delete the network from the archive.

        :param n: the network'''

        # delete the network record
        db.session.delete(n)

        # delete network file -- in this order to make
        # sure we don't end up with dangling files
        os.remove(n.network_filename())


class Tag(db.Model):
    '''A tag on a network. Tags are used for simple classification. Some
    are user-supplied; others are synthesised by the network analysers.
    '''

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True)

    @staticmethod
    def create_tag(tag):
        '''Ensure that a tag exists in the tags table. Tags are
        always normalised to be lower case.

        :param tag: the tag'''
        tag = tag.lower()
        t = Tag.query.filter_by(name=tag).first()
        if t is None:
            # no such tag, add it to the table
            t = Tag(name=tag)
            db.session.add(t)
        return t

    @staticmethod
    def ensure_tags(tags):
        '''Ensure all tags exist in the table.

        :param tags: a list of tags
        :returns: a list of Tag objects'''
        alltags = []
        for tag in tags:
            alltags.append(Tag.create_tag(tag))
        return alltags


class Metadata(db.Model):
    '''The metadata table.'''

    id = db.Column(db.Integer, primary_key=True)
    network_id = db.Column(db.ForeignKey('network.id'), nullable=False)
    network = db.relationship('Network',
                              backref=db.backref('metadata', lazy=True,
                                                 cascade='all, delete-orphan'),
                              cascade='all')
    key = db.Column(db.String(32), index=True)
    value = db.Column(db.String(128))
