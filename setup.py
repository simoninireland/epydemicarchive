# Setup for epydemicarchive
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

from setuptools import setup

with open('README.rst') as f:
    longDescription = f.read()

setup(name='epydemicarchive',
      version='0.2.1',
      description='Server for archives of complex networks',
      long_description=longDescription,
      url='http://github.com/simoninireland/epydemicarchive',
      author='Simon Dobson',
      author_email='simoninireland@gmail.com',
      license='License :: OSI Approved :: GNU General Public License v3 or later',
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Science/Research',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   'Programming Language :: Python :: 3.8',
                   'Programming Language :: Python :: 3.9',
                   'Topic :: Scientific/Engineering',
                   ],
      python_requires='>=3.6',
      packages=['epydemicarchive',
                'epydemicarchive.templates',
                'epydemicarchive.main',
                'epydemicarchive.main.templates',
                'epydemicarchive.main.pages',
                'epydemicarchive.auth',
                'epydemicarchive.auth.templates',
                'epydemicarchive.user',
                'epydemicarchive.user.templates',
                'epydemicarchive.archive',
                'epydemicarchive.archive.templates',
                'epydemicarchive.metadata',
                'epydemicarchive.api.v1',
                'epydemicarchive.api.v1.client',
                ],
      zip_safe=False,
      install_requires=["epydemic >= 1.7.1", "networkx >= 2.4", "numpy >= 1.18", "pyyaml", "pyopenssl", "python-dotenv", "flask", "flask-bootstrap", "flask-wtf", "email_validator", "flask-sqlalchemy", "flask-migrate", "flask-login", "flask-httpauth", "requests", "requests-toolbelt", ],
)
