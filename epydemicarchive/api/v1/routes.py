# Routes
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

import logging
from flask import jsonify, url_for, send_file, request
from werkzeug.http import HTTP_STATUS_CODES
from epydemicarchive import tokenauth
from epydemicarchive.api.v1 import api, __version__
from epydemicarchive.archive.models import Tag, Network


# Customise logging for API calls
logger = logging.getLogger(__name__)


# ---------- Error and authorisation failure handling ----------

def error(status, message=None):
    '''Create a standard-format error message.

    :param status: the HTTP status code
    :param message: the error message
    :returns: the formatted error'''
    payload = {
        '_version': __version__,
        'error': HTTP_STATUS_CODES.get(status, 'Unknown error')
    }
    if message:
        payload['message'] = message
    res = jsonify(payload)
    res.status_code = status
    return res


@tokenauth.error_handler
def token_error(status):
    '''Return an API error message for authorisation failure.

    :param status: the HTTP status code'''
    return error(status)


# ---------- API entry points ----------

@api.route('/tags', methods=['GET'])
@tokenauth.login_required
def tags():
    '''Return a list of tags.'''
    res = {
        '_version': __version__,
        'tags': [tag.name for tag in Tag.query.all()]
    }
    return jsonify(res)


@api.route('/networks', methods=['GET'])
@tokenauth.login_required
def networks():
    '''Return a list of all network UUIDs.'''
    res = {
        '_version': __version__,
        'uuids': [n.id for n in Network.query.all()]
    }
    return jsonify(res)


@api.route('/network/meta/<id>', methods=['GET'])
@tokenauth.login_required
def network(id):
    '''Retrieve the metadata for the given network.

    :param id: the network's UUID'''
    n = Network.query.filter_by(id=id).first()
    if n is None:
        return error(404, f'Network {id} not known')

    res = {
        '_version': __version__,
        'uuid': n.id,
        'uploaded': n.uploaded,
        'title': n.title,
        'description': n.description,
        'owner': n.owner.email,
        'tags': [tag.name for tag in n.tags],
        'metadata': {meta.key: meta.value for meta in n.metadata},
        '_links': {
            'raw': url_for('.raw', id=id),
        },
    }
    return jsonify(res)


@api.route('/network/raw/<id>')
@tokenauth.login_required
def raw(id):
    '''Return the network itself.

    :param id: the UUID of the network'''
    n = Network.query.filter_by(id=id).first()
    if n is None:
        return error(404, f'Network {id} not known')
    return send_file(n.network_filename())


@api.route('/network/submit', methods=['POST'])
@tokenauth.login_required
def submit():
    '''Submit a network to the archive.'''
    submission = request.form.to_dict()

    title = submission.get('title', '')
    description = submission.get('description', '')
    tags = submission.get('tags', [])
    extension = submission.get('extension', '')
