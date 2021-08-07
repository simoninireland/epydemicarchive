# Production server loader
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
import logging.handlers
from dotenv import load_dotenv
from epydemicarchive import create

# Load environment from .env
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
LOG_FILENAME = os.environ.get('LOGFILE') or 'ea.log'
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME,
                                                    when='midnight',
                                                    backupCount=7)
formatter = logging.Formatter('%(levelname)s:%(name)s: [%(asctime)s] %(message)s',
                              datefmt='%d/%b/%Y %H:%M:%S')
logger.addHandler(handler)
handler.setFormatter(formatter)

# create the Flask app
app = create()
