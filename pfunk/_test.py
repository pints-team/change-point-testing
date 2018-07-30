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


class AbstractFunctionalTest(object):
    """
    Abstract base class for functional tests or groups of tests.
    """
    def __init__(self, name):
        name = str(name)
        if pfunk.NAME_FORMAT.match(name) is None:
            raise ValueError('Invalid test name: ' + name)
        self._name = name

    def name(self):
        """ Runs this test's name. """
        return self._name

    def run(self):
        """ Runs this test and logs the output. """
        raise NotImplementedError


class FunctionalTest(AbstractFunctionalTest):
    """
    Abstract base class for single functional tests.
    """
    def _run(self, result_writer, log_path):
        raise NotImplementedError

    def run(self, date=None):
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
        date = date or pfunk.date()
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


class FunctionalTestGroup(AbstractFunctionalTest):
    """
    Group of tests to be run simultaneously.
    """
    def __init__(self, name, *tests):
        super(FunctionalTestGroup, self).__init__(name)
        self._tests = []
        for test in tests:
            if not isinstance(test, AbstractFunctionalTest):
                raise ValueError(
                    'All tests passed to a FunctionalTestGroup must extend'
                    ' AbstractFunctionalTest.')
            self._tests.append(test)

    def run(self):
        """ Runs this group of tests. """
        # Create logger for _global_ console/file output
        log = logging.getLogger(__name__)
        log.info('Running test group: ' + self.name())

        # Create test name
        date = pfunk.date()
        name = self.name()

        res_path = pfunk.unique_path(os.path.join(
            pfunk.DIR_RESULT, name + '-' + date + '.txt'))

        # Create result writer
        w = pfunk.ResultWriter(res_path)
        w['status'] = 'unitialised'
        w['date'] = date
        w['name'] = name

        # Run tests
        try:
            for test in self._tests:
                test.run(date=date)
        except Exception:
            log.error('Exception in test: ' + self.name())
            w['status'] = 'failed'
            raise
        finally:
            log.info('Writing result to ' + w.filename())
            w.write()

