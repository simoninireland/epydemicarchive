# Models
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

from epydemicarchive import db


class Metadata(db.Model):
    '''The metadata table.'''

    network_id = db.Column(db.ForeignKey('network.id'), nullable=False)
    network = db.relationship('Network', backref=db.backref('metadata', lazy=True))

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(32), index=True)
    value = db.Column(db.String(128))


    # ---------- Static helper methods ----------

    Chain = []

    @staticmethod
    def add_analyser(a):
        '''Add an analyser to the chain.

        :param a: the analyser'''
        Metadata.Chain.append(a)

    @staticmethod
    def analyse(n):
        '''Run the analysis chain over the given network, populating
        the metadata table appropriately.

        :param n: the network's archive record'''
        g = n.load_network()
        for a in Metadata.Chain:
            rc = a.do(n, g)
            for k in rc:
                m = Metadata(network=n,
                             key=k, value=str(rc[k]))
                db.session.add(m)
