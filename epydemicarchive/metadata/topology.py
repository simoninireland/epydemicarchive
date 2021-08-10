# Topology analyser
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

from numpy import mean, median, var
from epydemicarchive.metadata.analyser import Analyser


class Topology(Analyser):
    '''An analyser that extracts basic topological features and
    summary statistics.
    '''

    def do(self, n, g):
        '''Analyse the topology of the given network.

        :param n: the network
        :param g: the networkx representation of the network
        :returns: a dict of metadata'''
        topology = dict()

        # order
        topology['N'] = g.order()
        topology['M'] = g.number_of_edges()

        # extremal degrees
        degrees = sorted([d for (N, d) in list(g.degree)])
        topology['kmin'] = degrees[0]
        topology['kmax'] = degrees[-1]

        # degree summary statistics
        topology['kmean'] = mean(degrees)
        topology['kmedian'] = median(degrees)
        topology['kvar'] = var(degrees)

        return topology
