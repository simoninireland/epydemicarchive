# Makefile for epydemicarchive_client
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

# The name of our package on PyPi
PACKAGENAME = epydemicarchive_client

# The version we're building is inherited from parent build


# ----- Sources -----

# Source code
SOURCES_SETUP_IN = setup.py.in
SOURCES_PACKAGE = epydemicarchive/api/v1/client
SOURCES_CODE = \
	../$(SOURCES_PACKAGE)/__init__.py \
	../$(SOURCES_PACKAGE)/client.py

# Extras for the build and packaging system
SOURCES_EXTRA = \
	README.rst \
	LICENSE \
	HISTORY \
	CONTRIBUTORS
SOURCES_GENERATED = \
	MANIFEST \
	setup.py

# Distribution files
DIST_SDIST = dist/$(PACKAGENAME)-$(VERSION).tar.gz
DIST_WHEEL = dist/$(PACKAGENAME)-$(VERSION)-py3-none-any.whl


# ----- Tools -----

# Base commands
PYTHON = python3
FLASK = flask
PIP = pip
TWINE = twine
GPG = gpg
GIT = git
VIRTUALENV = $(PYTHON) -m venv
ACTIVATE = . $(VENV)/bin/activate
TR = tr
CAT = cat
SED = sed
RM = rm -fr
CP = cp -r
CHDIR = cd
MKDIR = mkdir -p
ZIP = zip -r

# Root directory
ROOT = $(shell pwd)

# Requirements and environment
VENV = ../venv3
REQUIREMENTS = requirements.txt

# Requirements for setup.py
# Note we elide dependencies to do with backporting the type-checking
PY_REQUIREMENTS = $(shell $(SED) -e '/^typing_extensions/d' -e 's/^\(.*\)/"\1",/g' $(REQUIREMENTS) | $(TR) '\n' ' ')

# Constructed commands
RUN_SETUP = $(PYTHON) setup.py
RUN_SPHINX_HTML = PYTHONPATH=$(ROOT) make html
RUN_TWINE = $(TWINE) upload dist/*


# ----- Top-level targets -----

# Default prints a help message
help:
	@make usage

# Build the API documentation using Sphinx
.PHONY: doc
doc: env $(SOURCES_DOCUMENTATION) $(SOURCES_DOC_CONF)
	$(ACTIVATE) && $(CHDIR) doc && $(RUN_SPHINX_HTML)

# Build a source distribution
sdist: localcopy $(DIST_SDIST)

# Build a wheel distribution
wheel: localcopy $(DIST_WHEEL)

# Build a local copy of the sources from the master tree
localcopy: $(SOURCES_CODE)
	$(MKDIR) $(SOURCES_PACKAGE)
	$(CP) $(SOURCES_CODE) ./$(SOURCES_PACKAGE)

# Upload a source distribution to PyPi
upload: sdist wheel
	$(GPG) --detach-sign -a dist/$(PACKAGENAME)-$(VERSION).tar.gz
	$(ACTIVATE) && $(RUN_TWINE)

# Clean up the distribution build
clean:
	$(RM) $(SOURCES_GENERATED) $(SOURCES_DIST_DIR) $(PACKAGENAME).egg-info dist $(SOURCES_DOC_BUILD_DIR) $(SOURCES_DOC_ZIP) epydemicarchive dist build


# ----- Generated files -----

# Manifest for the package
MANIFEST: Makefile
	echo  $(SOURCES_EXTRA) $(SOURCES_GENERATED) $(SOURCES_CODE) | $(TR) ' ' '\n' >$@

# The setup.py script
setup.py: $(SOURCES_SETUP_IN) $(REQUIREMENTS) Makefile
	$(CAT) $(SOURCES_SETUP_IN) | $(SED) -e 's|VERSION|$(VERSION)|g' -e 's|REQUIREMENTS|$(PY_REQUIREMENTS)|g' >$@

# The source distribution tarball
$(DIST_SDIST): $(SOURCES_GENERATED) $(SOURCES_CODE) Makefile
	$(ACTIVATE) && $(RUN_SETUP) sdist

# The binary (wheel) distribution
$(DIST_WHEEL): $(SOURCES_GENERATED) $(SOURCES_CODE) Makefile
	$(ACTIVATE) && $(RUN_SETUP) bdist_wheel


# ----- Usage -----

define HELP_MESSAGE
Available targets:
   make doc          build the API documentation using Sphinx
   make sdist        create a source distribution
   make wheel	     create binary (wheel) distribution
   make upload       upload distribution to PyPi
   make clean        clean the distribution

endef
export HELP_MESSAGE

usage:
	@echo "$$HELP_MESSAGE"
