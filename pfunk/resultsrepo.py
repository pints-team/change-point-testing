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
import logging
import socket

import pfunk


def commit_results():
    """
    Commits any new results.
    """
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

