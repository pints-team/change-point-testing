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

# Always import io
from . import io


# Set up logging
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
del(logging)


# Define log- and result directories
import os
DIR_PFUNK = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
DIR_LOG = os.path.join('logs')
DIR_RESULT = os.path.join('results')

# Ensure log- and result directories exist
if not os.path.isdir(DIR_LOG):
    log.info('Creating log dir: ' + DIR_LOG)
    os.makedirs(DIR_LOG)
if not os.path.isdir(DIR_RESULT):
    log.info('Creating result dir: ' + DIR_RESULT)
    os.makedirs(DIR_RESULT)
del(os)


# Date formatting
DATE_FORMAT = '%Y-%m-%d-%H:%M:%S'

def date():
    return time.strftime(DATE_FORMAT)


# Python version
import sys
PYTHON = sys.version.replace('\n', '')
del(sys)


# Pints version and hash
#TODO


# Import test class
from .test import FunctionalTest
