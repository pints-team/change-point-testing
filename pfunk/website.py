#
# Functions to interact with the Pints website.
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2019, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
import git
import logging
import subprocess

import pfunk


def upload_results():
    """
    Upload the generated plots and report file to the website.
    """
    # Get logger
    log = logging.getLogger(__name__)

    # Refresh website
    _refresh_repo()

    # Call the synchronisation script in a subprocess
    cmd = [pfunk.PATH_WEB_SYNC_SCRIPT]
    try:
        p = subprocess.Popen(cmd, cwd=pfunk.DIR_WEB_REPO)
        p.wait()
    except KeyboardInterrupt:
        p.terminate()
        log.error('Uploading aborted by user')
        return

    if p.returncode != 0:
        raise Exception(f'Upload script returned code {p.returncode}.')


def _refresh_repo():
    """ Pulls the website submodule. """
    log = logging.getLogger(__name__)

    log.info('Loading website repo')
    repo = git.Repo(pfunk.DIR_WEB_REPO)

    log.info('Checkout out master')
    repo.git.checkout('master')

    log.info('Perfoming git pull')
    log.info(repo.git.pull())
    log.info(repo.git.status())

