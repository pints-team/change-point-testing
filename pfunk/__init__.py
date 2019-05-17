#
# Pints functional testing module.
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2019, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
import logging
import os
import re
import sys
import time


# Require at least Python 3.6 (for importlib.reload and f-strings)
if not sys.version_info >= (3, 6):
    raise RuntimeError('Functional testing requires Python 3.6+')


# Set up logging
if 'PFUNK_DEBUG' in os.environ:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig()
log = logging.getLogger(__name__)
log.info('Loading Pints Functional Testing.')


# The root of this repository
DIR_PFUNK = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# The pints repository (submodule)
DIR_PINTS_REPO = os.path.join(DIR_PFUNK, 'pints')

# Location of the Pints module
DIR_PINTS_MODULE = os.path.join(DIR_PINTS_REPO, 'pints')

# The website repository (submodule)
DIR_WEB_REPO = os.path.join(DIR_PFUNK, 'website')

# The path to write plots and badges to
DIR_PLOT = os.path.join(DIR_WEB_REPO, 'static', 'functional-testing')

# The path to write the report to
PATH_REPORT = os.path.join(
    DIR_WEB_REPO, 'content', 'page', 'functional-testing.md')

# The path to the website sync script
PATH_WEB_SYNC_SCRIPT = os.path.join(DIR_WEB_REPO, 'z-deploy-funk.sh')


# Date formatting
DATE_FORMAT = '%Y-%m-%d-%H:%M:%S'


def date(when=None):
    if when:
        return time.strftime(DATE_FORMAT, when)
    else:
        return time.strftime(DATE_FORMAT)


# Test and plot name format (in regex form)
NAME_FORMAT = re.compile(r'^[a-zA-Z]\w*$')


# Default test results database path
# Used to store or retrieve test results, but can be overridden with the
# --database argument.
DEFAULT_RESULTS_DB = "./test_results.db"


# Python version
PYTHON_VERSION = sys.version.replace('\n', '')


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

# Commit message. We keep this because merges can change commit hashes, but the
# authored date and message will survive those. Of course, if you choose to
# interactively rebase and edit or squash the original commit, that's your
# choice.
PINTS_COMMIT_MESSAGE = None
PFUNK_COMMIT_MESSAGE = None


#
# Start importing sub modules
#
from . import (  # noqa
    pfunkrepo,
    pintsrepo,
    website,
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
    format_date,
    weave,
)

from ._test import (    # noqa
    FunctionalTest,
)
