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

from ._repotools import format_date


def headcommit():
    """
    Returns the current pfunk commit hash.
    """
    repo = git.Repo(pfunk.DIR_PFUNK)
    return repo.head.commit


def prepare_module():
    head = headcommit()
    pfunk.PFUNK_COMMIT = head.hexsha
    pfunk.PFUNK_COMMIT_COMMITTED = format_date(head.committed_date)
    pfunk.PFUNK_COMMIT_AUTHORED = format_date(head.authored_date)
    pfunk.PFUNK_COMMIT_MESSAGE = head.message
