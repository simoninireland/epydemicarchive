# Network analysers base class
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


class Analyser:
    '''An analyser is a class that examines a network submitted to
    the archive and determines something about its structure, which
    it then adds to the archive's metadata. Analysers are never
    called directly, but instead are registered with an instance of
    :class:`AnalyserChain` to be run when networks are uploaded.

    The actual analysis function is goven by overriding the :meth:`do`
    method, which is passed the network record in the archive and the
    `networkx` representaton of the network loaded from disc.
    '''

    def do(self, n, g):
        '''Analyse the given network. This should be overridden by sub-classes.

        :param n: the network
        :param g: the networkx representation of the network'''
        raise NotImplementedError('analyse')


class AnalyserChain:
    '''An analyser chain is a collection of :class:`Analyser`s run sequentially.
    '''

    def __init__(self, app=None):
        '''Create a new analyser chain.

        :param app: (optional) application to bind to'''
        self._db = None
        self._chain = []
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        '''Bind the analyser to an application.

        :param app: the application t bind to'''
        from epydemicarchive import db
        self._db = db
        self._chain = []

    def register_analyser(self, a):
        '''Add an analyser to the chain.

        :param a: the analyser'''
        self._chain.append(a)

    def analyse(self, n):
        '''Run the analysis chain over the given network, populating
        the metadata table appropriately.

        :param n: the network's archive record'''
        from epydemicarchive.archive.models import Metadata
        g = n.load_network()
        for a in self._chain:
            rc = a.do(n, g)
            for k in rc:
                m = Metadata(network=n,
                             key=k, value=str(rc[k]))
                self._db.session.add(m)
