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
from flask import render_template, url_for, redirect, abort
from epydemicarchive.main import main, pages_dir


@main.route('/')
@main.route('/index.html')
def index():
    '''The landing page for the site.'''
    return redirect(url_for('.page', pg='index.html'))


@main.route('/page/<pg>')
def page(pg):
    '''Render a page whose content is held statically within
    package, but that's rendered into a template for consistency.
    The static page is itself treated as a template, meaning it can
    contain generated links and the like.

    :param pg: the page'''
    filename = os.path.join(pages_dir, pg)
    if os.path.exists(filename):
        # suck in the page contents
        with open(filename, 'r') as f:
            page = '\n'.join(f.readlines())

        # render into the appropriate template
        return render_template('page.tmpl', page=page)

    # if we get here there's no such page
    abort(404)
