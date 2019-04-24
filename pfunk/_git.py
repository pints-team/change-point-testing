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
    # Ensure pints is up to date, and set PINTS_COMMIT to current hash
    if pfunk.PINTS_COMMIT is None or force_refresh:
        pfunk.pints_refresh()
        pfunk.PINTS_COMMIT = pfunk.pints_hash()

    # Set PINTS_VERSION to version indicated in the Pints module
    if pfunk.PINTS_VERSION is None or force_refresh:
        _set_pints_version_variable()


def _set_pints_version_variable():
    """
    Sets the PINTS_VERSION variable.
    """
    if pfunk.DIR_PINTS_REPO not in sys.path:
        sys.path.insert(0, pfunk.DIR_PINTS_REPO)

    import pints
    import importlib
    importlib.reload(pints)
    assert list(pints.__path__)[0] == pfunk.DIR_PINTS_MODULE
    pfunk.PINTS_VERSION = pints.version(formatted=True)


def pints_checkout(checkout):
    """
    Check out a specific commit, branch, or tree.
    """
    log = logging.getLogger(__name__)
    log.info('Checking out ' + str(checkout))

    # Check out requested commit, branch or tree
    repo = git.Repo(pfunk.DIR_PINTS_REPO)
    repo.git.checkout(checkout)

    # Set commit and version variables (will also reload Pints)
    pfunk.PINTS_COMMIT = pfunk.pints_hash()
    _set_pints_version_variable()

    # Show some nice info
    import time
    date = pfunk.date(time.gmtime(repo.head.commit.committed_date))
    log.info('Now at Pints commit ' + pfunk.PINTS_COMMIT)
    log.info('  Author: ' + repo.head.commit.author.name)
    log.info('  Date:   ' + date)
    log.info(repo.head.commit.message)


def pints_last_commits(n):
    """
    Returns the hashes of the last ``n`` commits in the Pints repo (master
    branch), sorted old-to-new.
    """
    n = int(n)
    assert n > 0
    repo = git.Repo(pfunk.DIR_PINTS_REPO)
    repo.git.checkout('master')
    commits = list(repo.iter_commits('master', max_count=n))
    commits.reverse()
    return [c.hexsha for c in commits]


def pints_commits_since(commit):
    """
    Returns the hashes of all commits since (and including) the given commit
    (specified as a hash) in the Pitns repo (master branch), sorted old-to-new.
    """
    repo = git.Repo(pfunk.DIR_PINTS_REPO)
    repo.git.checkout('master')

    found = False
    commits = []
    for c in repo.iter_commits('master'):
        commits.append(c.hexsha)
        if c.hexsha == commit:
            found = True
            break
    if not found:
        raise ValueError('Commit not found: ' + str(commit))

    commits.reverse()
    return commits


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

