#
# Fake test 1
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2018, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
from __future__ import absolute_import, division
from __future__ import print_function, unicode_literals

import os

import pfunk
import logging
import numpy as np


class FunctionalTest(object):
    """
    Abstract base class for functional tests.
    """

    def __init__(self, name):
        name = str(name)
        if pfunk.NAME_FORMAT.match(name) is None:
            raise ValueError('Invalid test name: ' + name)
        self._name = name

    def name(self):
        return self._name

    def _run(self, result_writer, log_path):
        raise NotImplementedError

    def run(self):
        """ Runs this test and logs the output. """
        # Create logger for _global_ console/file output
        log = logging.getLogger(__name__)
        log.info('Running test: ' + self.name())

        # Prepare to run
        pfunk.prepare_pints_repo()

        # Seed numpy random generator, so that we know the value
        seed = np.random.randint(2**32)    # Numpy says max seed is 2**32 - 1
        np.random.seed(seed)

        # Create test name
        date = pfunk.date()
        name = self.name()

        # Get path to log and result files
        base = name + '-' + date + '.txt'
        log_path = pfunk.unique_path(os.path.join(pfunk.DIR_LOG, base))
        res_path = pfunk.unique_path(os.path.join(pfunk.DIR_RESULT, base))

        # Create result writer
        w = pfunk.ResultWriter(res_path)
        w['status'] = 'unitialised'
        w['date'] = date
        w['name'] = name
        w['python'] = pfunk.PYTHON_VERSION
        w['pints'] = pfunk.PINTS_VERSION
        w['pints_commit'] = pfunk.PINTS_COMMIT
        w['seed'] = seed

        # Run test
        try:
            self._run(w, log_path)
        except Exception:
            log.error('Exception in test: ' + self.name())
            w['status'] = 'failed'
            raise
        finally:
            log.info('Writing result to ' + w.filename())
            w.write()

