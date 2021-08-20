# Archive query
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
from epydemicarchive.archive.models import Network, Tag, Metadata


class QueryNetworks:

    def __init__(self, tags, terms):
        self._tags = tags
        self._terms = terms

        # sd: we user outerjoin() here to get the networks that don't
        # have tags or metadata as well as those that do: join() would
        # discard the former
        self._q = Network.query.outerjoin(Network.tags)
        for tag in tags:
            self.add_tag(tag)
        self._q = self._q.outerjoin(Network.metadata)
        for term in terms:
            self.add_term(term)

    def add_tag(self, tag):
        self._q = self._q.filter(Tag.name == tag)

    def add_term(self, term):
        f = self.filter(term)
        self._q = f(self._q)

    def all(self):
        return list(self._q.all())

    def tags(self):
        return self._tags

    def terms(self):
        return self._terms

    def termstrings(self):
        return list(map(lambda t: '{k} {op} {v}'.format(k=t['key'],
                                                        op=t['operator'],
                                                        v=t['value']),
                        self._terms))

    def filter(self, term):
        op = term['operator']
        f = None
        if op == '==':
            f = self.query_equal
        elif op == '!=':
            f = self.query_notequal
        elif op == '<':
            f = self.query_lessthan
        elif op == '<=':
            f = self.query_lessthanorequal
        elif op == '>':
            f = self.query_greaterthan
        elif op == '>=':
            f = self.query_greaterthanorequal

        return f(term)

    def query_equal(self, term):
        def f(q):
            return q.filter(Metadata.key == term['key'],
                            Metadata.value == term['value'])
        return f

    def query_notequal(self, term):
        def f(q):
            return q.filter(Metadata.key == term['key'],
                            Metadata.value != term['value'])
        return f

    def query_lessthan(self, term):
        def f(q):
            return q.filter(Metadata.key == term['key'],
                            Metadata.value < term['value'])
        return f

    def query_lessthanorequal(self, term):
        def f(q):
            return q.filter(Metadata.key == term['key'],
                            Metadata.value <= term['value'])
        return f

    def query_greaterthan(self, term):
        def f(q):
            return q.filter(Metadata.key == term['key'],
                            Metadata.value > term['value'])
        return f

    def query_greaterthanorequal(self, term):
        def f(q):
            return q.filter(Metadata.key == term['key'],
                            Metadata.value >= term['value'])
        return f
