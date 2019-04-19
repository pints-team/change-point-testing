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
import re
import sys
import time
import logging


# Set up logging
if 'PFUNK_DEBUG' in os.environ:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig()
log = logging.getLogger(__name__)
log.info('Loading Pints Functional Testing.')


# Define directories to use
# The root of this repo
DIR_PFUNK = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# The root of the pints repo (submodule) and module
DIR_PINTS_REPO = os.path.join(DIR_PFUNK, 'pints')
DIR_PINTS_MODULE = os.path.join(DIR_PINTS_REPO, 'pints')
# The root of the results repo (submodule) and subdirectoroes
DIR_RES_REPO = os.path.join(DIR_PFUNK, 'res')
DIR_LOG = os.path.join(DIR_RES_REPO, 'logs')
DIR_RESULT = os.path.join(DIR_RES_REPO, 'results')
DIR_PLOT = os.path.join(DIR_RES_REPO, 'plots')


# Ensure log- and result directories exist
if not os.path.isdir(DIR_LOG):
    log.info('Creating log dir: ' + DIR_LOG)
    os.makedirs(DIR_LOG)
if not os.path.isdir(DIR_RESULT):
    log.info('Creating result dir: ' + DIR_RESULT)
    os.makedirs(DIR_RESULT)
if not os.path.isdir(DIR_PLOT):
    log.info('Creating plot dir: ' + DIR_PLOT)
    os.makedirs(DIR_PLOT)


# Date formatting
DATE_FORMAT = '%Y-%m-%d-%H:%M:%S'


def date(when=None):
    if when:
        return time.strftime(DATE_FORMAT, when)
    else:
        return time.strftime(DATE_FORMAT)


# Test and plot name format (in regex form)
NAME_FORMAT = re.compile(r'^[a-zA-Z]\w*$')


# Python version
PYTHON_VERSION = sys.version.replace('\n', '')


# Pints version and commit
# These are set using _git's function "prepare_pints_repo"
PINTS_COMMIT = PINTS_VERSION = None


#
# Start importing sub modules
#

# Always import io and git
from ._io import (  # noqa
    assert_not_deviated_from,
    find_next_test,
    find_previous_test,
    find_test_dates,
    find_test_results,
    gather_statistics_per_commit,
    generate_report,
    ResultWriter,
    unique_path,
)
from ._git import (  # noqa
    commit_results,
    pints_hash,
    pints_refresh,
    prepare_pints_repo,
    pfunk_hash,
)
from ._util import (  # noqa
    weave,
)

# Import test class
from ._test import (    # noqa
    FunctionalTest,
)


# PFunk commit
PFUNK_COMMIT = pfunk_hash()
