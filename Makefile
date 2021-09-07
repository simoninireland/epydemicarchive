# Makefile for epydemicarchive
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
PACKAGENAME = epydemicarchive

# The version we're building
VERSION = 0.2.1


# ----- Sources -----

# Source code
SOURCES_SETUP_IN = setup.py.in
SOURCES_PACKAGE = \
	epydemicarchive/__init__.py \
	epydemicarchive/templates/404.tmpl
SOURCES_MIGRATIONS = \
	migrations/README \
	migrations/alembic.ini \
	migrations/env.py \
	migrations/script.py.mako
SOURCES_DB_MIGRATIONS = \
	migrations/versions/af4c5eff0608_initial_models.py
SOURCES_MAIN_BLUEPRINT = \
	epydemicarchive/main/__init__.py \
	epydemicarchive/main/routes.py \
	epydemicarchive/main/templates/base.tmpl \
	epydemicarchive/main/templates/page.tmpl \
	epydemicarchive/main/pages/index.html
SOURCES_AUTH_BLUEPRINT = \
	epydemicarchive/auth/__init__.py \
	epydemicarchive/auth/models.py \
	epydemicarchive/auth/forms.py \
	epydemicarchive/auth/routes.py \
	epydemicarchive/auth/templates/login.tmpl \
	epydemicarchive/auth/templates/newuser.tmpl
SOURCES_USER_BLUEPRINT = \
	epydemicarchive/user/__init__.py \
	epydemicarchive/user/models.py \
	epydemicarchive/user/forms.py \
	epydemicarchive/user/routes.py \
	epydemicarchive/user/templates/profile_edit.tmpl
SOURCES_ARCHIVE_BLUEPRINT = \
	epydemicarchive/archive/__init__.py \
	epydemicarchive/archive/models.py \
	epydemicarchive/archive/forms.py \
	epydemicarchive/archive/queries.py \
	epydemicarchive/archive/routes.py \
	epydemicarchive/archive/templates/upload.tmpl \
	epydemicarchive/archive/templates/edit.tmpl \
	epydemicarchive/archive/templates/browse.tmpl \
	epydemicarchive/archive/templates/search.tmpl
SOURCES_METADATA_BLUEPRINT = \
	epydemicarchive/metadata/__init__.py \
	epydemicarchive/metadata/analyser.py \
	epydemicarchive/metadata/hash.py \
	epydemicarchive/metadata/topology.py \
	epydemicarchive/metadata/degreedistribution.py \
	epydemicarchive/metadata/er.py
SOURCES_API_V1_BLUEPRINT = \
	epydemicarchive/api/v1/__init__.py \
	epydemicarchive/api/v1/routes.py
SOURCES_API_V1_CLIENT = \
	epydemicarchive/api/v1/client/__init__.py \
	epydemicarchive/api/v1/client/client.py
SOURCES_CODE = \
	$(SOURCES_PACKAGE) \
	$(SOURCES_MIGRATIONS) \
	$(SOURCE_DB_MIGRATIONS) \
	$(SOURCES_MAIN_BLUEPRINT) \
	$(SOURCES_AUTH_BLUEPRINT) \
	$(SOURCES_USER_BLUEPRINT) \
	$(SOURCES_ARCHIVE_BLUEPRINT) \
	$(SOURCES_METADATA_BLUEPRINT) \
	$(SOURCES_API_V1_BLUEPRINT) \
	$(SOURCES_API_V1_CLIENT)
SOURCES_SERVER_TESTS =\
	test/test_api.py \
	test/test_search_api.py
SOURCES_TESTS = \
	test/app.py \
	test/test_query.py
FLASK_TEST_APP_INSTANCE = test.app:app

SOURCES_DOC_CONF = doc/conf.py
SOURCES_DOC_BUILD_DIR = doc/_build
SOURCES_DOC_BUILD_HTML_DIR = $(SOURCES_DOC_BUILD_DIR)/html
SOURCES_DOC_ZIP = $(PACKAGENAME)-doc-$(VERSION).zip
SOURCES_DOCUMENTATION = \
	doc/index.rst \

# Extras for the build and packaging system
SOURCES_EXTRA = \
	README.rst \
	LICENSE \
	HISTORY \
	CONTRIBUTORS
SOURCES_GENERATED = \
	MANIFEST \
	setup.py

# Default database, migrations, and file archive
NETWORKS_DB = ea.db
ARCHIVE_DIR = archive.d
MIGRATIONS_DIR = migrations

# Docker configuration
DOCKERFILE = Dockerfile
DOCKER_IMAGE = ea
DOCKER_BOOT = boot.sh

# Distribution files
DIST_SDIST = dist/$(PACKAGENAME)-$(VERSION).tar.gz
DIST_WHEEL = dist/$(PACKAGENAME)-$(VERSION)-py3-none-any.whl

# ----- Tools -----

# Base commands
PYTHON = python3
FLASK = flask
COVERAGE = coverage
PIP = pip
TWINE = twine
GPG = gpg
GIT = git
VIRTUALENV = $(PYTHON) -m venv
ACTIVATE = . $(VENV)/bin/activate
DOCKER = docker
TR = tr
CAT = cat
SED = sed
RM = rm -fr
CP = cp
CHDIR = cd
ZIP = zip -r
MKDIR = mkdir -p
WGET = wget
UNZIP = bsdtar -xvf-

# Files that are locally changed vs the remote repo
# (See https://unix.stackexchange.com/questions/155046/determine-if-git-working-directory-is-clean-from-a-script)
GIT_DIRTY = $(shell $(GIT) status --untracked-files=no --porcelain)

# Root directory
ROOT = $(shell pwd)

# Requirements for running the library and for the development venv needed to build it
VENV = venv3
REQUIREMENTS = requirements.txt
DEV_REQUIREMENTS = dev-requirements.txt

# Requirements for setup.py
# Note we elide dependencies to do with backporting the type-checking
PY_REQUIREMENTS = $(shell $(SED) -e '/^typing_extensions/d' -e 's/^\(.*\)/"\1",/g' $(REQUIREMENTS) | $(TR) '\n' ' ')

# Constructed commands
RUN_FLASK = FLASK_APP=$(FLASK_TEST_APP_INSTANCE) FLASK_ENV=development $(FLASK) run
RUN_SETUP = $(PYTHON) setup.py
RUN_TESTS = $(PYTHON) -m unittest discover -s test
RUN_SPHINX_HTML = PYTHONPATH=$(ROOT) make html
RUN_TWINE = $(TWINE) upload dist/*


# ----- Top-level targets -----

# Default prints a help message
help:
	@make usage

# Run a test server
live:
	$(ACTIVATE) && $(RUN_FLASK)

# Run a live server after reseting its environment
newlive:
	$(RM) $(NETWORKS_DB) $(MIGRATIONS_DIR) $(ARCHIVE_DIR)
	$(ACTIVATE) && FLASK_APP=$(FLASK_TEST_APP_INSTANCE) $(FLASK) db init
	$(ACTIVATE) && FLASK_APP=$(FLASK_TEST_APP_INSTANCE) $(FLASK) db migrate -m "initial setup"
	$(ACTIVATE) && FLASK_APP=$(FLASK_TEST_APP_INSTANCE) $(FLASK) db upgrade
	make live

# Run tests
test: env Makefile setup.py
	$(ACTIVATE) && $(RUN_TESTS)

.PHONY: server-test
server-test: env Makefile setup.py
	for s in $(SOURCES_SERVER_TESTS); do $(ACTIVATE) && PYTHONPATH=. $(PYTHON) $$s; done

# Build the API documentation using Sphinx
.PHONY: doc
doc: env $(SOURCES_DOCUMENTATION) $(SOURCES_DOC_CONF)
	$(ACTIVATE) && $(CHDIR) doc && $(RUN_SPHINX_HTML)

# Build a development venv from the requirements in the repo
.PHONY: env
env: $(VENV)

$(VENV):
	$(VIRTUALENV) $(VENV)
	$(CAT) $(REQUIREMENTS) $(DEV_REQUIREMENTS) >$(VENV)/requirements.txt
	$(ACTIVATE) && $(PIP) install -U pip wheel && $(CHDIR) $(VENV) && $(PIP) install -r requirements.txt

# Build a source distribution
sdist: $(DIST_SDIST)

# Build a wheel distribution
wheel: $(DIST_WHEEL)

# Build the client-side API
client: commit
	$(CHDIR) client && make sdist wheel VERSION=$(VERSION)

# Upload a source distribution to PyPi
upload: commit sdist wheel
	$(GPG) --detach-sign -a dist/$(PACKAGENAME)-$(VERSION).tar.gz
	$(ACTIVATE) && $(RUN_TWINE)

# Update the remote repos on release
commit: check-local-repo-clean
	$(GIT) push origin master
	$(GIT) tag -a v$(VERSION) -m "Version $(VERSION)"
	$(GIT) push origin v$(VERSION)

.SILENT: check-local-repo-clean
check-local-repo-clean:
	if [ "$(GIT_DIRTY)" ]; then echo "Uncommitted files: $(GIT_DIRTY)"; exit 1; fi

# Build a docker image
docker-image: $(SOURCES_CODE) Makefile $(DOCKERFILE)
	$(DOCKER) build -t $(DOCKER_IMAGE):latest -t $(DOCKER_IMAGE):$(VERSION) .

# Run the server live in a Docker container
docker-live:
	$(DOCKER) run --name ea -p 8050:5000 --mount type=bind,source="$(ROOT)",target=/home/ea/data --rm $(DOCKER_IMAGE):latest

# Clean up the distribution build
clean:
	$(RM) $(SOURCES_GENERATED) $(SOURCES_DIST_DIR) $(PACKAGENAME).egg-info dist $(SOURCES_DOC_BUILD_DIR) $(SOURCES_DOC_ZIP) dist build

# Clean up everything, including the computational environment (which is expensive to rebuild)
reallyclean: clean
	$(RM) $(VENV) $(ARCHIVE_JS_PLUGIN_DIR)


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
   make live         run a test server (NOT FOR PRODUCTION)
   make test         run the API test suite
   make doc          build the API documentation using Sphinx
   make env          create a development virtual environment
   make sdist        create a source distribution
   make wheel	     create binary (wheel) distribution
   make upload       upload distribution to PyPi
   make client       upload the client-side API as epydemicarchive_client
   make commit       tag current version and and push to master repo
   make docker-image build a Docker image
   make docker-live  run a test server in a Docker container
   make clean        clean-up the build
   make reallyclean  clean up the virtualenv as well

endef
export HELP_MESSAGE

usage:
	@echo "$$HELP_MESSAGE"
