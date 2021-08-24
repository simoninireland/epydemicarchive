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

from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from epydemicarchive import db
from epydemicarchive.auth.models import User
from epydemicarchive.user import user
from epydemicarchive.user.forms import EditProfile
from epydemicarchive.user.models import Profile


@user.route('/profile/<email>', methods=['GET', 'POST'])
@login_required
def profile(email):
    '''The user profile editing page.'''
    u = User.from_email(email)
    if u is None:
        flash('User {email} not known', 'error')
        return redirect(url_for('main.index'))
    profile = Profile.from_user(u)

    # populate the form
    form = EditProfile(data=dict(name=profile.name,
                                 affiliation=profile.affiliation,
                                 url=profile.url,
                                 bio=profile.bio))

    if form.validate_on_submit():
        if form.cancel.data:
            # user cancelled editing
            flash('Profile edit cancelled', 'info')
        elif current_user != u:
            # attempt to edit someone else's profile
            flash('Can\'t edit someone else\'s profile!', 'error')
            return redirect(url_for('main.index'))
        elif form.api_key.data:
            # user requested a new API key
            u.revoke_api_key()
            u.get_api_key()
            db.session.commit()
            flash('New API key generated (old key has been revoked)', 'success')
            return redirect(url_for('.edit_profile', email=email))
        else:
            # copy in the new data
            profile.name = form.name.data
            profile.affiliation = form.affiliation.data
            profile.url = form.url.data
            profile.bio = form.bio.data
            db.session.commit()

            flash(f'Profile edited for {email}', 'success')

        # jump back to home page
        return redirect(url_for('main.index'))

    return render_template('profile_edit.tmpl', title='Edit profile',
                           user=u, profile=profile, form=form)
