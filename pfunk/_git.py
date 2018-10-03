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


def pfunk_hash():
    """
    Returns the current pfunk commit hash.
    """
    repo = git.Repo(pfunk.DIR_PFUNK)
    return str(repo.head.commit.hexsha)


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

    log.info('Checking out master branch')
    repo = git.Repo(pfunk.DIR_PINTS_REPO)
    repo.git.checkout('master')

    log.info('Perfoming git pull')
    log.info(repo.git.pull())


def prepare_pints_repo(force_refresh=False):
    """
    Makes sure Pints is up to date. Should be run before importing pints.
    """
    # Ensure pints is up to date
    if pfunk.PINTS_COMMIT is None or force_refresh:
        pfunk.pints_refresh()
        pfunk.PINTS_COMMIT = pfunk.pints_hash()

    # Get Pints version from local repo
    if pfunk.PINTS_VERSION is None:
        sys.path.insert(0, pfunk.DIR_PINTS_REPO)
        import pints
        import importlib
        importlib.reload(pints)
        assert list(pints.__path__)[0] == pfunk.DIR_PINTS_MODULE
        pfunk.PINTS_VERSION = pints.version(formatted=True)
    elif force_refresh:
        import pints
        import importlib
        importlib.reload(pints)
        pfunk.PINTS_VERSION = pints.version(formatted=True)


def commit_results():
    """
    Commits any new results
    """
    import socket
    message = 'New results (' + socket.gethostname() + ' ' + pfunk.date() + ')'

    log = logging.getLogger(__name__)

    log.info('Loading results repo')
    repo = git.Repo(pfunk.DIR_RES_REPO)

    log.info('Checkout out master')
    repo.git.checkout('master')

    log.info('Checking for changes')
    if not (repo.is_dirty() or repo.untracked_files):
        log.info('No changes found')
        return

    log.info('Perfoming git pull')
    log.info(repo.git.pull())

    log.info('Perfoming git add')
    log.info(repo.git.add(pfunk.DIR_RES_REPO))
    log.info(repo.git.status())

    log.info('Performing git commit')
    log.info(repo.git.commit('-m', message))

    log.info('Performing git push')
    log.info(repo.git.push())

