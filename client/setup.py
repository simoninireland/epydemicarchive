# Setup for epydemicarchive-client
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

setup(name = 'epydemicarchive-client',
      version = '0.1.1',
      description = 'Client for the epydemic archive',
      long_description = longDescription,
      url = 'http://github.com/simoninireland/epydemicarchive',
      author = 'Simon Dobson',
      author_email = 'simoninireland@gmail.com',
      license = 'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
      classifiers = [ 'Development Status :: 4 - Beta',
                      'Intended Audience :: Science/Research',
                      'Intended Audience :: Developers',
                      'Programming Language :: Python :: 3.6',
                      'Programming Language :: Python :: 3.7',
                      'Programming Language :: Python :: 3.8',
                      'Programming Language :: Python :: 3.9',
                      'Topic :: Scientific/Engineering' ],
      python_requires = '>=3.6',
      packages = [ 'epydemicarchive.api.v1.client' ],
      zip_safe = False,
      install_requires = [ "networkx >= 2.4", "requests", "requests-toolbelt",  ],
)
