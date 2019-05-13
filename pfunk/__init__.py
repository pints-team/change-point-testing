#
# Pints functional testing module.
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2019, University of Oxford.
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
_DIR_RESULT_DEFAULT = os.path.join(DIR_RES_REPO, 'results')
DIR_RESULT = _DIR_RESULT_DEFAULT
_DIR_PLOT_DEFAULT = os.path.join(DIR_RES_REPO, 'plots')
DIR_PLOT = _DIR_PLOT_DEFAULT


# Ensure result and plot directories exist
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


# Require at least Python 3.4 (for importlib.reload)
if not sys.version_info >= (3, 4):
    raise RuntimeError('Functional testing requires Python 3.4+')


# Default test results database path
# Used to store or retrieve test results, but can be overridden with the --database argument.
DEFAULT_RESULTS_DB = "./test_results.db"

# Pints version and pints/pfunk commits
# These are set using (repo).prepare_module

# Pints version string
PINTS_VERSION = None

# Commit hashes
PINTS_COMMIT = None
PFUNK_COMMIT = None

# Date commit was authored (patch or original commit was created)
PINTS_COMMIT_AUTHORED = None
PFUNK_COMMIT_AUTHORED = None

# Date commit was committed (the last time the commit was edited)
PINTS_COMMIT_COMMITTED = None
PFUNK_COMMIT_COMMITTED = None

# Commit message. We keep this because merges can change commit hashes, but the authored date and message will survive
# those. Of course, if you choose to interactive rebase and edit or squash the original commit, that's your choice.
PINTS_COMMIT_MESSAGE = None
PFUNK_COMMIT_MESSAGE = None


#
# Start importing sub modules
#
from . import (  # noqa
    pfunkrepo,
    pintsrepo,
    resultsrepo,
)

from ._io import (  # noqa
    assert_not_deviated_from,
    clean_filename,
    find_next_test,
    find_previous_test,
    gather_statistics_per_commit,
    generate_report,
    unique_path,
)

from ._resultsdb import (  # noqa
    ResultsDatabaseWriter,
    find_test_results,
    find_test_dates,
)

from ._util import (  # noqa
    weave,
)

from ._test import (    # noqa
    FunctionalTest,
)

from ._repotools import (    # noqa
    format_date,
)