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

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from epydemicarchive import db
from epydemicarchive.auth import auth
from epydemicarchive.auth.forms import Login, Register
from epydemicarchive.auth.models import User


@auth.route('/login', methods=['GET', 'POST'])
def login():
    '''The login page.'''

    # if user is already logged in, do nothing
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # show login form
    form = Login()
    if form.validate_on_submit():
        # check whether we have the right email address and password
        email = form.email.data
        u = User.from_email(email)
        if u is None or not u.check_password(form.password.data):
            # passwords don't match, jump back to login page
            flash('Email and password for {u} don\'t match'.format(u=email), 'error')
            return redirect(url_for('auth.login'))

        # jump to the page the user was trying to access
        login_user(u, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        flash('User {u} signed in'.format(u=email), 'success')
        return redirect(next_page)

    return render_template('login.tmpl', title='Sign in', form=form)


@auth.route('/logout')
def logout():
    '''The logout page.'''
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    '''The user registration page.'''
    form = Register()
    if form.validate_on_submit():
        # create the user
        id = User.create_user(form.email.data, form.password.data)
        db.session.commit()

        # jump back to home page
        flash(f'User {id} created', 'success')
        return redirect(url_for('main.index'))

    return render_template('newuser.tmpl', title='Register', form=form)
