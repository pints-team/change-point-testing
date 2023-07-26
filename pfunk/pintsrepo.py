#
# Git functions for the Pints repository.
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2019, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
import git
import importlib
import logging
import sys
import textwrap
import time

import pfunk


def head():
    """
    Returns the current pints commit object.
    """
    repo = git.Repo(pfunk.DIR_PINTS_REPO)
    return repo.head.commit


def hash():
    """
    Returns the current pints commit hash.
    """
    repo = git.Repo(pfunk.DIR_PINTS_REPO)
    return str(repo.head.commit.hexsha)


def info():
    """
    Returns a multi-line string with information about the currently selected
    pints commit.
    """
    c = git.Repo(pfunk.DIR_PINTS_REPO).head.commit
    lines = []
    lines.append('commit ' + str(c.hexsha))
    lines.append('Author: ' + c.author.name)
    lines.append('Date:   ' + pfunk.date(time.gmtime(c.authored_date)))
    lines.append('')
    w = textwrap.TextWrapper()
    w.initial_indent = w.subsequent_indent = '    '
    lines.extend(w.wrap(c.message))
    lines.append('')
    return '\n'.join(lines)


def pull():
    """
    Pulls remote changes and checks out the latest commit from main.
    """
    log = logging.getLogger(__name__)

    log.info('Checking out main branch')
    repo = git.Repo(pfunk.DIR_PINTS_REPO)
    repo.git.checkout('main')

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
    #log = logging.getLogger(__name__)

    # Add the repo version of python to the system path, ensuring this is
    # preferred over a globally installed Pints.
    if pfunk.DIR_PINTS_REPO not in sys.path:
        sys.path.insert(0, pfunk.DIR_PINTS_REPO)

    # Make sure pints can be loaded
    import pints
    importlib.reload(pints)

    # Check that we're using the local version of Pints, not an installed one
    assert list(pints.__path__)[0] == pfunk.DIR_PINTS_MODULE

    # Set identifying variables
    pfunk.PINTS_COMMIT = pfunk.pintsrepo.hash()
    pfunk.PINTS_COMMIT_AUTHORED = pfunk.format_date(
        pfunk.pintsrepo.head().authored_date)
    pfunk.PINTS_COMMIT_COMMITTED = pfunk.format_date(
        pfunk.pintsrepo.head().committed_date)
    pfunk.PINTS_COMMIT_MESSAGE = pfunk.pintsrepo.head().message
    pfunk.PINTS_VERSION = pints.version(formatted=True)


def latest_commits(n):
    """
    Returns the hashes of the last ``n`` commits in the Pints repo (main
    branch), sorted old-to-new.
    """
    n = int(n)
    assert n > 0
    repo = git.Repo(pfunk.DIR_PINTS_REPO)
    repo.git.checkout('main')
    commits = list(repo.iter_commits('main', max_count=n))
    commits.reverse()
    return [c.hexsha for c in commits]


def commits_since(commit):
    """
    Returns the hashes of all commits since (and including) the given commit
    (specified as a hash) in the Pitns repo (main branch), sorted old-to-new.
    """
    repo = git.Repo(pfunk.DIR_PINTS_REPO)
    repo.git.checkout('main')

    found = False
    commits = []
    for c in repo.iter_commits('main'):
        commits.append(c.hexsha)
        if c.hexsha == commit:
            found = True
            break
    if not found:
        raise ValueError('Commit not found: ' + str(commit))

    commits.reverse()
    return commits

