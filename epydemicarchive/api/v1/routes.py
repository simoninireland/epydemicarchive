# Routes
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

import logging
import random
from flask import jsonify, url_for, send_file, request
from werkzeug.http import HTTP_STATUS_CODES
from markupsafe import escape
from epydemicarchive import tokenauth, db, analyser
from epydemicarchive.api.v1 import api, __version__
from epydemicarchive.archive.models import Tag, Network, Metadata
from epydemicarchive.archive.queries import QueryNetworks
from epydemicarchive.auth.models import User
from epydemicarchive.metadata.analyser import Analyser


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
    logger.error(message)
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


@api.route('/network/info/<id>', methods=['GET'])
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
    n = Network.from_uuid(id)
    if n is None:
        return error(404, f'Network {id} not known')
    return send_file(n.network_filename())


@api.route('/submit', methods=['POST'])
@tokenauth.login_required
def submit():
    '''Submit a network to the archive.'''
    user = tokenauth.current_user()
    email = user.email

    # retrieve the metadata for the submission
    submission = request.form
    filename = submission.get('filename')
    if filename is None:
        return error(400, 'No filename given for submitted network (can\'t determine file type)')
    title = escape(submission.get('title', ''))
    description = escape(submission.get('description', ''))
    tags = map(escape, submission.get('tags', '').split(','))

    # retieve raw network_filename
    if 'raw' not in request.files:
        return error(400, 'No submitted network')
    raw = request.files['raw']

    # create the network
    n = Network.create_network(user,
                               filename,
                               raw,
                               title,
                               description,
                               tags)
    uuid = n.id

    # extract metadata for the network
    # TODO: this should be asynchronous
    analyser.analyse(n)

    db.session.commit()
    logging.info(f'Network {uuid} submitted by {email}')

    # return the UUID for the newly-created network
    res = {
        '_version': __version__,
        'uuid': uuid
        }
    return jsonify(res)


@api.route('/search', methods=['POST'])
@tokenauth.login_required
def search():
    '''Grab one or more networks from the archive according to the given
    specification. The specification can provide tags and metadata,
    as well as limiting the pool of networks to choose from and
    excluding networks already used. It returns the UUID of a network(s)
    matching the criteria, which may then be retrieved using the 'raw'
    endpoint.

    '''

    # retrieve the query
    if not request.is_json:
        return error(400, 'Not a JSON query')
    query = request.get_json()

    # version check
    v = query.get('_version', __version__)
    if v != __version__:
        return error(400, 'API version mismatch ({c} used against {s})'.format(c=v,
                                                                               s=__version__))

    # determine how many networks we're looking for, with -1 signifiying all
    n = query.get('n', -1)

    # perform the query against the archive
    tags = query.get('tags', [])
    metadata = query.get('metadata', [])
    qn = QueryNetworks(tags, metadata)
    networks = list(qn.all())

    # do any requested exclusions
    exclude = query.get('exclude', None)
    if exclude is not None:
        # exclude any networks from the pool
        ex = set(exclude)
        networks = [n for n in networks if n.id not in ex]

    # return the networks
    if n > 0:
        # we need to make a random choice
        # check the size of the pool
        pool = query.get('pool', n)
        if pool < n:
            # need a pool at least as large as the set of networks
            # we want to draw
            res = {
                '_version': __version__,
                'message': f'Need a pool of at least {n} from which to draw {n} networks'
            }
            return jsonify(res)
        if pool > 0 and len(networks) < pool:
            # we don't have a large enough pool of
            # matching networks to draw from
            res = {
                '_version': __version__,
                'message': 'Insufficient pool of networks to draw from'
            }
            return jsonify(res)

        # draw from the pool
        networks = random.sample(networks, k=n)

    # return the chosen network's UUID
    # TODO: add links to raw and info endpoints
    res = {
        '_version': __version__,
        'uuids': [n.id for n in networks],
    }
    return jsonify(res)
