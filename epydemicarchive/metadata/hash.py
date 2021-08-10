# Hash generator
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

from hashlib import sha256
from epydemicarchive.metadata.analyser import Analyser


class Hash(Analyser):
    '''An analyser that computes the SHA256 hash of the underlying
    network's on-disc representation. This reads the file again and
    so is potentially expensive when applied to large networks.
    '''

    CHUNKSIZE = 4096    #: Size of chunks to read from file.

    def do(self, n, g):
        '''Analyse the topology of the given network.

        :param n: the network
        :param g: the networkx representation of the network (unused)
        :returns: a dict of metadata'''
        filename = n.network_filename()
        h = sha256()
        with open(filename, 'rb') as fh:
            while True:
                bs = fh.read(self.CHUNKSIZE)
                if len(bs) == 0:
                    break
                h.update(bs)

        rc = {'sha256': h.hexdigest()}
        return rc
