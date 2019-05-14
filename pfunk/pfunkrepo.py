#
# Git functions for the PFunk repository
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2019, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
from __future__ import absolute_import, division
from __future__ import print_function, unicode_literals

import git
import pfunk


def head():
    """
    Returns the current pfunk commit object.
    """
    repo = git.Repo(pfunk.DIR_PFUNK)
    return repo.head.commit


def prepare_module():
    headcommit = head()
    pfunk.PFUNK_COMMIT = headcommit.hexsha
    pfunk.PFUNK_COMMIT_COMMITTED = pfunk.format_date(headcommit.committed_date)
    pfunk.PFUNK_COMMIT_AUTHORED = pfunk.format_date(headcommit.authored_date)
    pfunk.PFUNK_COMMIT_MESSAGE = headcommit.message
