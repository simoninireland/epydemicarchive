# Client-side of the API
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
from tempfile import NamedTemporaryFile
from copy import copy
from urllib.parse import urljoin
import json
import requests
from requests_toolbelt import MultipartEncoder
from networkx import write_adjlist, read_adjlist


class Archive:
    '''A client-side representation of an epydemic archive.

    If the base URI is not provided it is loaded from the SERVER_URI
    environment variable.  If the API key is not provided it is loaded
    from the API_KEY environment variable. This allows programs that
    populate an archive to be configured from their runtime
    environment.  Exceptions are raised if these values aren't
    available.

    :param uri: (optional) the base URI of the archive
    :param api_key: (optional) the API key to authenticate against the archive
    '''

    # Tuning parameters
    CHUNKSIZE = 4096                       #: Chunk size for streaming networks from the archive.
    FILETYPE = '.al.gz'                    #: Default file type for submitted networks.

    # The base URI for the API
    API = '/api/v1'                        #: The file part of the API base URI.

    def __init__(self, uri=None, api_key=None):
        # store the API key
        if api_key is None:
            api_key = os.environ.get('API_KEY')
            if api_key is None:
                raise Exception('No API_KEY available')
        self._api_key = api_key
        self._headers = dict()
        self._headers['Authorization'] = 'Bearer {k}'.format(k=self._api_key)

        # get the URI
        if uri is None:
            uri = os.environ.get('SERVER_URI')
            if uri is None:
                raise Exception('No SERVER_URI available')
        self._base_uri = urljoin(uri, self.API)

    def base_uri(self):
        '''Return the base URI used to access this archive. This is
        a combination of the archive URI and the namespace for the
        endpoints of the current version of the API.

        :returns: the base URI'''
        return self._base_uri

    def endpoint(self, meth, arg=None):
        '''Return the URI associatedx with the given method.

        :param meth: the method
        :param arg: the argument (defaults to none)
        :returns: a URI'''
        if arg is not None:
            meth = meth + '/' + arg
        m = urljoin(self._base_uri, self.API + meth)
        return m

    def tags(self):
        '''Return all the tags applied to networks in the archive.

        :returns: a list of tags'''
        url = self.endpoint('/tags')
        r = requests.get(url,
                         headers=self._headers)
        r.raise_for_status()
        res = r.json()
        return res['tags']

    def networks(self):
        '''Return all the network UUIDs for networks in the archive.

        :returns: a list of UUIDs'''
        url = self.endpoint('/networks')
        r = requests.get(url,
                         headers=self._headers)
        r.raise_for_status()
        res = r.json()
        return res['uuids']

    def info(self, uuid):
        '''Return a dict of information about the given network.

        :param uuid the network's UUID
        :returns: a dict of information'''
        url = self.endpoint('/network/info', uuid)
        r = requests.get(url,
                         headers=self._headers)
        r.raise_for_status()
        return r.json()

    def raw(self, uuid):
        '''Retreve and load the network with the given UUID.

        :param uuid: the network's UUID
        :returns: the networkx representation of the network'''
        filename = None
        try:
            # create a tremporary file to hold the downloaded network
            with NamedTemporaryFile(delete=False) as tf:
                filename = tf.name

            # make the request
            url = self.endpoint('/network/raw', uuid)
            r = requests.get(url,
                             headers=self._headers,
                             stream=True)
            r.raise_for_status()

            # stream the result into the file
            with open(filename, 'wb') as wh:
                for chunk in r.iter_content(chunk_size=self.CHUNKSIZE):
                    wh.write(chunk)

            # load the network
            g = read_adjlist(filename)
            return g
        finally:
            if filename is not None:
                os.remove(filename)

    def submit(self, g, title='', desc='', tags=[]):
        '''Submit a network to the archive.

        :param g: the network
        :param title: (optional) title for the network
        :param desc: (optional) descrriptionfor the network
        :param tags: (optional) tags to be applied to the network
        :returns: the UUID of the submitted network'''
        filename = None
        try:
            # write the network to a temporary file ready to stream
            with NamedTemporaryFile(suffix=self.FILETYPE, mode='wb', delete=False) as tf:
                filename = tf.name
            # sd: we have to close the file and write to it by name to get
            # automatic compression of the resulting network
            write_adjlist(g, filename)

            # create the request
            # sd: this uses a multipart encoder to allow a large
            # network file to be streamed rather than read into memory twice
            encoder = MultipartEncoder({
                'filename': filename,
                'title': title,
                'description': desc,
                'tags': ','.join(tags),
                'raw': (filename, open(filename, 'rb'), 'application/octet-stream'),
            })
            headers = copy(self._headers)
            headers['Content-type'] = encoder.content_type

            # make the request
            url = self.endpoint('/submit')
            r = requests.post(url,
                              headers=headers,
                              data=encoder)
            r.raise_for_status()

            # return the UUID of the newly-created network
            rc = r.json()
            return rc['uuid']
        finally:
            if filename is not None:
                os.remove(filename)

    def search(self, tags=[], metadata=[], exclude=None, n=None, pool=None):
        '''Search the archive for a number of networks matching the given
        criteria. The size of pool from which to draw can be set to ensure
        enough randomness; networks previously used can be excluded from any
        selection to prevent re-use.

        Metadata constraints take the form of a list of triples where
        each triple is of the form:

        (<variable>, <operator>, <value>)

        where <operator> is one of ==, !=, <, <=, >, >=.

        :param tags: (optional) the tags that must be present (defaults to none)
        :param metadata: (optional) metadata constraints (defaults to none)
        :param exclude: (optional) list of network UUIDs to exclude
        :param n: (optional) number of networks to retrieve (defaults to all)
        :param pool: (optional) minimum pool of networks to draw from'''

        # build the query
        query = {
            'tags': tags,
            }
        if n is not None:
            query['n'] = n
        if metadata is not None:
            query['metadata'] = [
                {
                    'key': kv[0],
                    'operator': kv[1],
                    'value': kv[2]
                } for kv in metadata]
        if exclude is not None:
            query['exclude'] = exclude
        if pool is not None:
            query['pool'] = pool

        # make the request
        url = self.endpoint('/search')
        headers = copy(self._headers)
        headers['Content-type'] = 'application/json'
        r = requests.post(url,
                          headers=headers,
                          data=json.dumps(query))
        r.raise_for_status()

        # return the UUIDs of the drawn networks
        rc = r.json()
        return rc.get('uuids', [])
