# Erdos-Renyi network analyser
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

from epydemic.gf import gf_er
from epydemicarchive.metadata.analyser import Analyser
from epydemicarchive.metadata.degreedistribution import DegreeDistribution


class ER(DegreeDistribution):
    '''An analyser that checks for Erdos-Renyi degree topology.
    '''

    def do(self, n, g):
        '''Compare the degree distribution of the network against
        that expected of an ER network.

        :param n: the network
        :param g: the networkx representation of the network
        :returns: a dict of metadata'''
        er = dict()

        N = int(n['N'])
        kmean = float(n['kmean'])
        gf = gf_er(N, kmean)
        if self.significance(g, gf):
            er['degree-distribution'] = 'ER'

        return er
