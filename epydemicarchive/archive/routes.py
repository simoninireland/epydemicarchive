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
from flask import render_template, flash, redirect, url_for, send_file
from flask_login import current_user
from epydemicarchive import db
from epydemicarchive.archive import archive
from epydemicarchive.archive.forms import UploadNetwork, EditNetwork
from epydemicarchive.archive.models import Network
from epydemicarchive.metadata.analyser import Analyser

logger = logging.getLogger(__name__)


@archive.route('/upload', methods=['GET', 'POST'])
def upload():
    '''Upload a network manually, optionally providing title and tags.'''
    form = UploadNetwork()

    if form.validate_on_submit():
        try:
            # create the network
            n = Network.create_network(form.file.data.filename,
                                       form.file.data,
                                       form.title.data,
                                       form.description.data,
                                       form.tags.data)
            id = n.id

            # extract metadata for the network
            # TODO: this should be asynchronous
            Analyser.analyse(n)

            db.session.commit()
            flash(f'New network uploaded as {id}', 'success')
            logger.info(f'Network {id} uploaded')
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
                                 tags=', '.join(n.tagnames())))

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
            # TODO: should be confirmed,preferably in-line
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
                    n.title = form.title.data
                    n.description = form.description.data
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
