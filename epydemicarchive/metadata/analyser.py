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

from epydemicarchive import db


class Analyser:
    '''An analyser is a class that examines a network submitted to
    the archive and determines something about its structure, which
    it then adds to the archive's metadata.
    '''

    def do(self, id, g):
        '''Analyse the given network. This should be overridden by sub-classes.

        :param id: the UUID of the network
        :param g: the network'''
        raise NotImplementedError('analyse')
