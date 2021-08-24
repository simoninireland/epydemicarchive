# Test the query function
#
# Copyright (C) 2021 Simon Dobson
#
# This file is part of epydemicarchive, a server for complex network archives.
#
# epydemicarchive is free software: you can redistribute it and/or modify
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
from statistics import mean
from tempfile import NamedTemporaryFile, mkdtemp
import unittest
from networkx import fast_gnp_random_graph, write_adjlist
from epydemicarchive import create, Config, db, analyser
from epydemicarchive.auth.models import User
from epydemicarchive.archive.models import Network, Metadata
from epydemicarchive.archive.queries import QueryNetworks


class MockFileUpload:
    '''A mock-up of the Flask file upload object, requiring a save() method.'''

    CHUNKSIZE = 4096

    def __init__(self, filename):
        self._fn = filename

    def save(self, filename):
        with open(filename, 'wb') as wh:
            with open(self._fn, 'rb') as rh:
                while True:
                    chunk = rh.read(self.CHUNKSIZE)
                    if len(chunk) == 0:
                        break
                    wh.write(chunk)


class TestQuery(unittest.TestCase):

    def __init__(self, suite):
        super().__init__(suite)

        # configure for transient in-memory database and archive
        Config.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        Config.ARCHIVE_DIR = mkdtemp()
        Config.HOST = 'localhost'
        Config.PORT = 5050
        app = create(Config)
        self.app = app

        # set up a simple test database
        with app.app_context():
            # create the tables
            db.create_all()

            # add a test user
            self.u = User.create_user('test@test.com', 'xxx')
            self.email = self.u.email
            self.api_key = self.u.api_key

            # add some test networks
            self.g1 = fast_gnp_random_graph(500, 0.02)
            self.addNetwork(self.g1, ['random', 'er'])
            self.g2 = fast_gnp_random_graph(5000, 0.02)
            self.addNetwork(self.g2, ['random'])
            self.g3 = fast_gnp_random_graph(500, 0.02)
            self.addNetwork(self.g3, ['test'])
            self.g4 = fast_gnp_random_graph(500, 0.02)
            self.addNetwork(self.g4, ['test', 'bonus'])

            # commit the database
            db.session.commit()

    def addNetwork(self, g, tags):
        filename = None
        try:
            with NamedTemporaryFile(suffix='.al.gz', delete=False) as tf:
                filename = tf.name
            write_adjlist(g, filename)

            # create the network
            n = Network.create_network(self.u,
                                       filename,
                                       MockFileUpload(filename),
                                       'A test network',
                                       'A network',
                                       tags)

            # run the analysis chain over the new network
            analyser.analyse(n)
        finally:
            if filename is not None:
                os.remove(filename)

    def testTagQuery(self):
        '''Test we can extract by a single tag.'''
        with self.app.app_context():
            gs = QueryNetworks(tags=['random']).all()
            self.assertEqual(len(gs), 2)

    def testTagsQuery(self):
        '''Test we can extract by a several tags.'''
        with self.app.app_context():
            gs = QueryNetworks(tags=['er', 'random']).all()
            self.assertEqual(len(gs), 1)

    def testTagsQueryNone(self):
        '''Test we can extract non-matching tags.'''
        with self.app.app_context():
            gs = QueryNetworks(tags=['test', 'random']).all()
            self.assertEqual(len(gs), 0)

    def testSingleQuery(self):
        '''Test we can extract a network from a simple query.'''
        with self.app.app_context():
            constraints = [('N', '<=', 1000)]
            metadata = [{'key': t[0],
                         'operator': t[1],
                         'value': t[2]} for t in constraints]
            gs = QueryNetworks(constraints=metadata).all()
            self.assertEqual(len(gs), 3)

    def testMultipleQuery(self):
        '''Test we can extract a network from a compound query.'''
        with self.app.app_context():
            degrees = [d for (_, d) in list(self.g1.degree)]
            kmean = mean(degrees)

            constraints = [('N', '<=', 1000),
                           ('kmean', '>=', int(kmean * 0.5)),
                           ('kmean', '<=', int(kmean * 1.5))]
            metadata = [{'key': t[0],
                         'operator': t[1],
                         'value': t[2]} for t in constraints]
            gs = QueryNetworks(constraints=metadata).all()
            self.assertEqual(len(gs), 3)

    def testMultipleQueryNoSolution(self):
        '''Test we can extract a network from a compound quer with no solutiony.'''
        with self.app.app_context():
            degrees = [d for (_, d) in list(self.g1.degree)]
            kmean = mean(degrees)

            constraints = [('N', '>', 5000),
                           ('kmean', '>=', int(kmean * 0.5)),
                           ('kmean', '<=', int(kmean * 1.5))]
            metadata = [{'key': t[0],
                         'operator': t[1],
                         'value': t[2]} for t in constraints]
            gs = QueryNetworks(constraints=metadata).all()
            self.assertEqual(len(gs), 0)

    def testMultipleQueryTags(self):
        '''Test we can extract a network from a compound query with tags too.'''
        with self.app.app_context():
            degrees = [d for (_, d) in list(self.g1.degree)]
            kmean = mean(degrees)

            tags = ['random']
            constraints = [('N', '<=', 1000),
                           ('kmean', '>=', int(kmean * 0.5)),
                           ('kmean', '<=', int(kmean * 1.5))]
            metadata = [{'key': t[0],
                         'operator': t[1],
                         'value': t[2]} for t in constraints]
            gs = QueryNetworks(tags=tags, constraints=metadata).all()
            self.assertEqual(len(gs), 1)


if __name__ == '__main__':
    unittest.main()
