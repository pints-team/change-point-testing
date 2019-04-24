#
# Git functions for the Pints repository.
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2019, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
from __future__ import absolute_import, division
from __future__ import print_function, unicode_literals

import importlib
import git
import logging
import sys

from IPython.lib import deepreload

import pfunk


def hash():
    """
    Returns the current pints commit hash.
    """
    repo = git.Repo(pfunk.DIR_PINTS_REPO)
    return str(repo.head.commit.hexsha)


def pull():
    """
    Pulls remote changes and checks out the latest commit from master.
    """
    log = logging.getLogger(__name__)

    log.info('Checking out master branch')
    repo = git.Repo(pfunk.DIR_PINTS_REPO)
    repo.git.checkout('master')

    log.info('Perfoming git pull')
    log.info(repo.git.pull())


def checkout(checkout):
    """
    Checks out a specific commit, branch, or tree.
    """
    log = logging.getLogger(__name__)
    log.info('Checking out ' + str(checkout))

    # Check out requested commit, branch or tree
    repo = git.Repo(pfunk.DIR_PINTS_REPO)
    repo.git.checkout(checkout)


def prepare_module():
    """
    Prepares the Pints module for import (reloading if necessary).
    """
    log = logging.getLogger(__name__)

    # Add the repo version of python to the system path, ensuring this is
    # preferred over a globally installed Pints.
    if pfunk.DIR_PINTS_REPO not in sys.path:
        sys.path.insert(0, pfunk.DIR_PINTS_REPO)

    # Make sure pints can be loaded
    try:
        import pints
        importlib.reload(pints)
    except ImportError as e:
        log.info('Pints reload failed, performing deep reload')
        deepreload.reload(pints, exclude=(
            'sys',
            'os.path',
            'builtins',
            '__main__',
            'numpy',
            'numpy._globals',
            'scipy',
            'cma',
            'importlib',
            'importlib._bootstrap',
        ))

    # Check that we're using the local version of Pints, not an installed one
    assert list(pints.__path__)[0] == pfunk.DIR_PINTS_MODULE

    # Set identifying variables
    pfunk.PINTS_COMMIT = pfunk.pintsrepo.hash()
    pfunk.PINTS_VERSION = pints.version(formatted=True)


def latest_commits(n):
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


def commits_since(commit):
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

