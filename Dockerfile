# Dockerfile for epydemicarchive
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

FROM python:slim

RUN useradd ea
WORKDIR /home/ea

ENV FLASK_APP ea.py
ENV SECRET_KEY aaaabbbbccc
ENV DATABASE_URI sqlite:////home/ea/ea.db
ENV ARCHIVE_DIR /home/ea/archive.d

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install wheel
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY epydemicarchive epydemicarchive
COPY migrations migrations
COPY ea.py boot.sh ./
RUN chmod +x boot.sh

RUN chown -R ea:ea ./

USER ea
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
