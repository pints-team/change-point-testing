#
# Git module.
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2018, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
from __future__ import absolute_import, division
from __future__ import print_function, unicode_literals

#import os
#import sys
import logging
import git

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
    logging.basicConfig()
    log = logging.getLogger(__name__)
    log.info('Perfoming git pull')

    repo = git.Repo(pfunk.DIR_PINTS_REPO)
    log.info(repo.git.pull())

