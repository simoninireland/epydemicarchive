# Degree distribution analyser base class
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

from collections import Counter
from numpy import mean
from scipy.stats import chisquare
from epydemicarchive.metadata.analyser import Analyser


class DegreeDistribution(Analyser):
    '''Base class for analysers that classify the degree distribution of
    a network.
    '''

    SIGNIFICANCE = 0.05    #: P-value at which to reject the null hypothesis (5%).

    def significance(self, g, gf):
        '''Compare the degree distribution of the network against
        that described by the given generating function.

        :param g: the networkx representation of the network
        :param gf: the theoretical degree distribution
        :returns: True if the network's distribution is as expected'''
        dist = dict()

        # construct the degree histogram of the network
        N = g.order()
        seq = sorted([d for (_, d) in g.degree()])
        kmean = mean(seq)
        hist = Counter(seq)
        maxk = max(seq)
        d_network = [hist[i] for i in range(maxk + 1)]

        # construct the theoretical degree histogram
        d_theory = [int(gf[k] * N) for k in range(maxk + 1)]

        # remove any expected-zero degrees
        # sd: this seems like it could go wrong in some instances,
        # but scipy requires that there are no zeros in the expected
        # distribution
        remove = []
        for k in range(maxk + 1):
            if d_theory[k] == 0:
                remove.append(k - len(remove))
        for k in remove:
            del d_network[k]
            del d_theory[k]

        # perform a chi-squared test on the samples
        (_, p) = chisquare(d_network, d_theory)
        print(p)

        # for a goodness-of-fit test we reject the null hypothesis (that
        # the samples come from the expected distribution) for p-values
        # less that the chosen significance value
        return p > self.SIGNIFICANCE
