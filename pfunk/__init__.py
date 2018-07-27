#
# Pints functional testing module.
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2018, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
from __future__ import absolute_import, division
from __future__ import print_function, unicode_literals

import os
import sys
import logging


# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
log.info('Loading Pints Functional Testing.')


# Define directories to use
DIR_PFUNK = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DIR_LOG = os.path.join(DIR_PFUNK, 'logs')
DIR_RESULT = os.path.join(DIR_PFUNK, 'results')
DIR_PINTS_REPO = os.path.join(DIR_PFUNK, 'pints')
DIR_PINTS_MODULE = os.path.join(DIR_PINTS_REPO, 'pints')


# Ensure log- and result directories exist
if not os.path.isdir(DIR_LOG):
    log.info('Creating log dir: ' + DIR_LOG)
    os.makedirs(DIR_LOG)
if not os.path.isdir(DIR_RESULT):
    log.info('Creating result dir: ' + DIR_RESULT)
    os.makedirs(DIR_RESULT)


# Date formatting
DATE_FORMAT = '%Y-%m-%d-%H:%M:%S'

def date():
    return time.strftime(DATE_FORMAT)


# Python version
import sys
PYTHON_VERSION = sys.version.replace('\n', '')


#
# Start importing sub modules
#

# Always import io and git
from . import io
from . import git


# Ensure pints is up to date
git.pints_refresh()


# Get Pints commit hash from git module
PINTS_COMMIT = git.pints_hash()


# Get Pints version from local repo
sys.path.insert(0, DIR_PINTS_REPO)
import pints
assert pints.__path__[0] == DIR_PINTS_MODULE
PINTS_VERSION = pints.version(formatted=True)


# Import test class
from .test import FunctionalTest

