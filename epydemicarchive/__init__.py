# Server initialisation
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
import tempfile
from dotenv import load_dotenv
from flask import Flask, Blueprint, redirect, render_template, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_httpauth import HTTPTokenAuth


# Load environment from .env
load_dotenv()


# Load configuration from environment
class Config:
    # Web forms
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'A secret'

    # Database connection and tweaks
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///' + tempfile.mkstemp(suffix='.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Directory for storing networks
    ARCHIVE_DIR = os.environ.get('ARCHIVE_DIR') or tempfile.mkdtemp()


# Instanciate all the extensions
bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view='auth.login'
tokenauth = HTTPTokenAuth()


# Make sure the archive directory exists
dir = Config.ARCHIVE_DIR
if not os.path.exists(dir):
    try:
        os.makedirs(dir)
    except os.OSError as e:
        # failed to create, log and re-raise
        raise e


# Applicationn factory
def create(config=Config):
    # create the top-level app
    app = Flask(__name__)

    # configure app, using static configuration as the default
    app.config.from_object(config)

    # bind the extensions to the app
    bootstrap.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # register blueprints
    from epydemicarchive.main import main
    app.register_blueprint(main)
    from epydemicarchive.auth import auth
    app.register_blueprint(auth, url_prefix='/auth')
    from epydemicarchive.user import user
    app.register_blueprint(user, url_prefix='/user')
    from epydemicarchive.archive import archive
    app.register_blueprint(archive, url_prefix='/archive')
    from epydemicarchive.api.v1 import api as api_v1
    app.register_blueprint(api_v1, url_prefix='/api/v1')

    # custom error handlers
    def page_not_found(e):
        return render_template('404.tmpl'), 404
    app.register_error_handler(404, page_not_found)

    return app
