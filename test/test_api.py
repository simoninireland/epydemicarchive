# API tests
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
from tempfile import NamedTemporaryFile, mkdtemp
from unittest import makeSuite, TextTestRunner
from networkx import fast_gnp_random_graph, write_adjlist
from flask_unittest import LiveTestCase, LiveTestSuite
from epydemicarchive import create, Config, db
from epydemicarchive.api.v1.client import Archive
from epydemicarchive.auth.models import User
from epydemicarchive.archive.models import Network


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


class TestAPI(LiveTestCase):

    def setUp(self):
        '''Create a client-side archive object.'''
        self._archive = Archive('http://{h}:{p}'.format(h=Config.HOST,
                                                        p=Config.PORT),
                                self.api_key)

    def testUnauthorised(self):
        '''Test we can't do unauthorised access.'''
        self._archive._headers = []
        with self.assertRaises(Exception):
            self._archive.tags()

    def testTags(self):
        '''Test we can retrieve their tags.'''
        tags = self._archive.tags()
        self.assertCountEqual(tags, ['er', 'test'])

    def testNetworks(self):
        '''Test we can find the test network.'''
        networks = self._archive.networks()
        self.assertCountEqual(networks, [self.uuid])

    def testInfo(self):
        '''Test we cen retrieve network information.'''
        info = self._archive.info(self.uuid)
        for t in ['uuid', 'title', 'description', 'owner', 'tags', 'metadata']:
            self.assertIn(t, info)
        self.assertEqual(info['uuid'], self.uuid)
        self.assertEqual(info['owner'], self.email)
        self.assertCountEqual(info['tags'], ['test', 'er'])
        self.assertCountEqual(info['metadata'], {})   # no analyser chain to fill in metadata

    def testRaw(self):
        '''Test we can get the same network back.'''
        gprime = self._archive.raw(self.uuid)
        self.assertEqual(self.g.order(), gprime.order())
        # need more checks

    def testSubmit(self):
        '''Test we can submit and retrieve a network.'''
        h = fast_gnp_random_graph(500, 0.02)
        uuid = self._archive.submit(h, title='Another network', tags=['er'])
        hprime = self._archive.raw(uuid)
        self.assertEqual(h.order(), hprime.order())
        info = self._archive.info(uuid)
        self.assertEqual(info['title'], 'Another network')
        self.assertEqual(info['description'], '')
        self.assertCountEqual(info['tags'], ['er'])


if __name__ == '__main__':
    # configure for transient in-memory database and archive
    Config.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    Config.ARCHIVE_DIR = mkdtemp()
    Config.HOST = 'localhost'
    Config.PORT = 5050
    app = create(Config)

    # set up a simple test database
    with app.app_context():
        # create the tables
        db.create_all()

        # add a test user
        u = User.create_user('test@test.com', 'xxx')
        TestAPI.email = u.email
        TestAPI.api_key = u.api_key
        db.session.add(u)

        # add a network
        filename = None
        try:
            # create a temporary file to take the graph
            with NamedTemporaryFile(suffix='.al', delete=False) as tf:
                filename = tf.name

            # create the network
            TestAPI.g = fast_gnp_random_graph(200, 0.01)
            write_adjlist(TestAPI.g, filename)

            # create the network
            n = Network.create_network(u,
                                       filename,
                                       MockFileUpload(filename),
                                       'A test network',
                                       'A network',
                                       ['test', 'er'])
            TestAPI.uuid = n.id
            db.session.add(n)
        finally:
            if filename is not None:
                os.remove(filename)

        # commit the database
        db.session.commit()

    # create and run the test suite
    suite = LiveTestSuite(app)
    suite.addTest(makeSuite(TestAPI))
    runner = TextTestRunner(verbosity=2)
    runner.run(suite)
