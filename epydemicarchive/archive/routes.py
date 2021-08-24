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

import os
import logging
from flask import render_template, flash, redirect, url_for, send_file, session
from flask_login import current_user
from wtforms import FormField
from markupsafe import escape
from epydemicarchive import db, analyser
from epydemicarchive.archive import archive
from epydemicarchive.archive.forms import UploadNetwork, EditNetwork, SearchNetworks
from epydemicarchive.archive.models import Network, Tag
from epydemicarchive.archive.queries import QueryNetworks

logger = logging.getLogger(__name__)


@archive.route('/upload', methods=['GET', 'POST'])
def upload():
    '''Upload a network manually, optionally providing title and tags.'''
    form = UploadNetwork()

    if form.validate_on_submit():
        try:
            # create the network
            n = Network.create_network(current_user,
                                       form.file.data.filename,
                                       form.file.data,
                                       escape(form.title.data),
                                       escape(form.description.data),
                                       list(map(escape, form.tags.data)))
            uuid = n.id

            # extract metadata for the network
            # TODO: this should be asynchronous
            analyser.analyse(n)

            db.session.commit()
            flash(f'New network uploaded as {uuid}', 'success')
            logger.info(f'Network {uuid} uploaded')
        except Exception as e:
            flash(f'Problem uploading network: {e}', 'error')

        # jump back to home page
        return redirect(url_for('main.index'))

    return render_template('upload.tmpl', title='Upload a network', form=form)


@archive.route('/browse')
def browse():
    '''Browse all the available networks.'''
    networks = Network.query.all()
    return render_template('browse.tmpl', title='Browse networks', networks=networks)


@archive.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    '''Edit the data associated with the given network.

    :param id: the network UUID'''
    n = Network.from_uuid(id)
    if n is None:
        flash(f'Network {id} is not in the archive', 'error')
        return redirect(url_for('.browse'))

    # populate the form
    form = EditNetwork(data=dict(title=n.title,
                                 description=n.description,
                                 tags=n.tagnames()))

    if form.validate_on_submit():
        # the first two commands are always available
        if form.cancel.data:
            # user cancelled, return to browsing
            if current_user == n.owner:
                flash('Edit cancelled', 'info')
        elif form.download.data:
            # user downloaded network, send as a file
            return send_file(n.network_filename(), as_attachment=True)

        # the next two commands are only available to the owner of
        # the network. They are only presented to the owner in the
        # edit.tmpl template, but we check again to guard against hacks
        # that submit a request in other ways
        # TODO: flask_principal should help against this?
        elif form.delete.data:
            # user deletes network
            # TODO: should be confirmed, preferably in-line
            if current_user == n.owner:
                Network.delete_network(n)
                db.session.commit()

                flash(f'Network {id} deleted', 'success')
                logger.info(f'Network {id} deleted')
            else:
                flash(f'Can\'t delete a network you don\'t own', 'error')
        else:
            if current_user == n.owner:
                try:
                    # copy in new data
                    n.title = escape(form.title.data)
                    n.description = escape(form.description.data)
                    n.tags = Tag.ensure_tags(form.tags.data)

                    db.session.commit()

                    flash('Network metadata edited', 'success')
                    logger.info(f'Network {id} metadata edited')
                except Exception as e:
                    flash(f'Problem editing network: {e}', 'error')
            else:
                flash(f'Can\'t edit a network you don\'t own', 'error')

        # jump back to browsing page
        return redirect(url_for('.browse'))

    return render_template('edit.tmpl', title='Edit network', network=n, form=form)


@archive.route('/search', methods=['GET', 'POST'])
def search():
    '''Search the archive.'''
    session['tags'] = []
    session['metadata'] = []
    return redirect(url_for('.refine'))


@archive.route('/refine', methods=['GET', 'POST'])
def refine():
    '''Search the archive, using tags and metadata values to narrow the choice.'''
    tags = session.get('tags', [])
    metadata = session.get('metadata', [])

    # restrict the networks according to the current constraints
    qn = QueryNetworks(tags, metadata)
    networks = qn.all()

    # populate the form
    form = SearchNetworks()
    form.tags.data = qn.tags()
    form.metadata.data = ', '.join(qn.constraintstrings())

    if form.validate_on_submit():
        if form.refine.data:
            if form.add_tag.data:
                # additional tags
                # sd: can't directly append to the list in the session object
                tags.append(form.add_tag.data)
                session['tags'] = tags
            elif form.add_meta_key:
                # additional metadata
                # sd: can't directly append to the list in the session object
                k = form.add_meta_key.data
                v = form.add_meta_value.data
                metadata.append({'key': k,
                                 'operator': '==',
                                 'value': v})
                session['metadata'] = metadata

            return redirect(url_for('.refine'))

        elif form.reset.data:
            # reset the query
            print('reset')
            return redirect(url_for('.search'))

    return render_template('search.tmpl', title='Search the archive',
                           networks=networks,
                           form=form)
