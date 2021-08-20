# Search API tests
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
from epydemicarchive import create, Config, db, analyser
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

    def testSelectSingle(self):
        '''Test we can select a single network.'''
        uuids = self._archive.search(tags=['er'])
        self.assertCountEqual(uuids, [TestAPI.uuid])

    def testSelectNone(self):
        '''Test we can fail to find a network with the given tags.'''
        uuids = self._archive.search(tags=['plc'])
        self.assertNotIn('uuids', uuids)

    def testSelectOneFromTwo(self):
        '''Test we can select one network from a possible two.'''
        g = fast_gnp_random_graph(500, 0.02)
        gid = self._archive.submit(g, title='A network', tags=['select'])
        h = fast_gnp_random_graph(500, 0.02)
        hid = self._archive.submit(h, title='Another network', tags=['select'])

        # check we get both
        uuids = self._archive.search(tags=['select'])
        self.assertCountEqual(uuids, [hid, gid])

        # check we can pick one
        uuids = self._archive.search(n=1, tags=['select'])
        self.assertEqual(len(uuids), 1)
        self.assertIn(uuids[0], [hid, gid])

    def testSelectPool(self):
        '''Test we can restrict the pool from which we draw.'''
        g = fast_gnp_random_graph(500, 0.02)
        gid = self._archive.submit(g, title='A network', tags=['pooled'])
        h = fast_gnp_random_graph(500, 0.02)
        hid = self._archive.submit(h, title='Another network', tags=['pooled'])
        k = fast_gnp_random_graph(500, 0.02)
        kid = self._archive.submit(k, title='A third network', tags=['pooled'])

        # draw one from three
        uuids = self._archive.search(n=1, tags=['pooled'])
        self.assertEqual(len(uuids), 1)
        self.assertIn(uuids[0], [hid, gid, kid])

        # draw one from two
        uuids = self._archive.search(n=1, pool=2, tags=['pooled'])
        self.assertEqual(len(uuids), 1)
        self.assertIn(uuids[0], [hid, gid, kid])

        # draw three from three
        uuids = self._archive.search(n=3, tags=['pooled'])
        self.assertCountEqual(uuids, [hid, gid, kid])

        # too small a pool
        uuids = self._archive.search(n=1, pool=5, tags=['pooled'])
        self.assertEqual(len(uuids), 0)

    def testSelectMetadata(self):
        '''Test metadata selection.'''
        uuids = self._archive.search(metadata=[('N', '>=', TestAPI.g.order())])
        self.assertCountEqual(uuids, [TestAPI.uuid])

    def testSelectOperators(self):
        '''Test the different metadata operators.'''
        g = fast_gnp_random_graph(100, 0.5)
        gid = self._archive.submit(g, title='A network', tags=['comp'])
        h = fast_gnp_random_graph(300, 0.02)
        hid = self._archive.submit(h, title='Another network', tags=['comp'])
        k = fast_gnp_random_graph(500, 0.02)
        kid = self._archive.submit(k, title='A third network', tags=['comp'])

        uuids = self._archive.search(tags=['comp'], metadata=[('N', '==', g.order())])
        self.assertCountEqual(uuids, [gid])
        uuids = self._archive.search(tags=['comp'], metadata=[('N', '==', k.order())])
        self.assertCountEqual(uuids, [kid])

        uuids = self._archive.search(tags=['comp'], metadata=[('N', '>', 450)])
        self.assertCountEqual(uuids, [kid])
        uuids = self._archive.search(tags=['comp'], metadata=[('N', '>', 250)])
        self.assertCountEqual(uuids, [hid, kid])
        #uuids = self._archive.search(tags=['comp'], metadata=[('N', '>', g.order() - 20)])
        #self.assertCountEqual(uuids, [hid, kid, gid])

        uuids = self._archive.search(tags=['comp'], metadata=[('N', '>=', 100)])
        self.assertCountEqual(uuids, [hid, kid, gid])
        uuids = self._archive.search(tags=['comp'], metadata=[('N', '>=', 150)])
        self.assertCountEqual(uuids, [hid, kid])

        uuids = self._archive.search(tags=['comp'], metadata=[('N', '<', 350)])
        self.assertCountEqual(uuids, [hid, gid])
        uuids = self._archive.search(tags=['comp'], metadata=[('N', '<', 5000)])
        self.assertCountEqual(uuids, [hid, gid, kid])

        uuids = self._archive.search(tags=['comp'], metadata=[('N', '>', 100),
                                                              ('N', '<', 450)])
        self.assertCountEqual(uuids, [hid])


if __name__ == '__main__':
    # configure for transient in-memory database and archive
    Config.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    Config.ARCHIVE_DIR = mkdtemp()
    Config.HOST = 'localhost'
    Config.PORT = 5050
    app = create(Config)
    TestAPI._app = app

    # set up a simple test database
    with app.app_context():
        # create the tables
        db.create_all()

        # add a test user
        u = User.create_user('test@test.com', 'xxx')
        TestAPI.email = u.email
        TestAPI.api_key = u.api_key

        # add a network
        filename = None
        try:
            # create a temporary file to take the graph
            with NamedTemporaryFile(suffix='.al.gz', delete=False) as tf:
                filename = tf.name
            print(filename)

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

            # run the analysis chain over the new network
            analyser.analyse(n)
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
