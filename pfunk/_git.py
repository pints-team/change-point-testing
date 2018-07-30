#
# Git functions.
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2018, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
from __future__ import absolute_import, division
from __future__ import print_function, unicode_literals

import git
import sys
import logging

import pfunk


def pints_hash():
    """
    Returns the current pints commit hash.
    """
    repo = git.Repo(pfunk.DIR_PINTS_REPO)
    return str(repo.head.commit.hexsha)


def pints_refresh():
    """
    Updates the local pints repo.
    """
    log = logging.getLogger(__name__)
    log.info('Perfoming git pull')

    repo = git.Repo(pfunk.DIR_PINTS_REPO)
    log.info(repo.git.pull())


def prepare_pints_repo():
    """
    Makes sure Pints is up to date. Should be run before importing pints.
    """
    # Ensure pints is up to date
    if pfunk.PINTS_COMMIT is None:
        pfunk.pints_refresh()
        pfunk.PINTS_COMMIT = pfunk.pints_hash()

    # Get Pints version from local repo
    if pfunk.PINTS_VERSION is None:
        sys.path.insert(0, pfunk.DIR_PINTS_REPO)
        import pints
        assert pints.__path__[0] == pfunk.DIR_PINTS_MODULE
        pfunk.PINTS_VERSION = pints.version(formatted=True)

