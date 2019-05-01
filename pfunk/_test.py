#
# Lists all tests.
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2019, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
from __future__ import absolute_import, division
from __future__ import print_function, unicode_literals

import os

import glob
import pfunk
import logging
import numpy as np


class FunctionalTest(object):
    """
    Abstract base class for single functional tests.
    """
    def __init__(self, name, writer_generator):
        name = str(name)
        if pfunk.NAME_FORMAT.match(name) is None:
            raise ValueError('Invalid test name: ' + name)
        self._name = name
        self._writer_generator = writer_generator

    def _analyse(self, results):
        """
        This will be defined for an indiviual test. It will analyse the outputs
        of a given test and determine if that test passed or failed

        Args:

        results -- the results from all the previously run tests (see
        :meth:`pfunk.find_test_results`)

        Returns:

        bool -- True if test has passed, False otherwise
        """
        raise NotImplementedError

    def analyse(self):
        """
        Checks if the test passed or failed

        At the moment this just prints if the test has passed or failed. This
        should do something more intelligent, e.g. email someone
        """

        # Create logger for _global_ console/file output
        log = logging.getLogger(__name__)
        log.info('Running analyse: ' + self.name())

        # Load test results
        results = pfunk.find_test_results(self._name)

        # Analyse
        result = False
        try:
            result = self._analyse(results)
        except Exception:
            log.error('Exception in analyse: ' + self.name())
            raise
        finally:
            if result:
                log.info('Test ' + self.name() + ' has passed')
            else:
                log.info('Test ' + self.name() + ' has failed')

        # Return
        return result

    def name(self):
        """
        Runs this test's name.
        """
        return self._name

    def _plot(self, results):
        """
        This will be defined for an indiviual test. It will generate a single
        plot, or multiple plots for each test using the previous test results.

        Args:

        results -- the results from all the previously run tests (see
        :meth:`pfunk.find_test_results`)

        Returns:

        Matplotlib Figure or Iterable of Matplotlib Figures

        """
        raise NotImplementedError

    def plot(self, show=False):
        """
        Generates the plots defined for this test

        All plots returned by the test are written out to a filename defined
        by the test name and current date. If ``show==True`` then the figures
        are also shown on the current display.
        """
        # Create logger for _global_ console/file output
        log = logging.getLogger(__name__)
        log.info('Running plot: ' + self.name())

        # Load test results
        results = pfunk.find_test_results(self._name)

        # Plot
        try:
            figs = self._plot(results)
        except Exception:
            log.error('Exception in plot: ' + self.name())
            raise

        # Create path (assuming 1 figure; will fix with unique_path if more)
        date = pfunk.date()
        name = self.name()
        path = name + '-' + date + '.png'

        # Store names of generated files and glob mask of pathname to delete
        # old figures later
        generated = []
        mask = name + '-' + '*.png'

        try:
            # Assume that the user returns an iterable object containing
            # figures
            for i, fig in enumerate(figs):
                plot_path = pfunk.unique_path(
                    os.path.join(pfunk.DIR_PLOT, path))
                log.info('Storing plot: ' + plot_path)
                fig.savefig(plot_path)
                generated.append(plot_path)
        except TypeError:
            # If not, then assume that the user returns a single figure
            plot_path = pfunk.unique_path(os.path.join(pfunk.DIR_PLOT, path))
            log.info('Storing plot: ' + plot_path)
            figs.savefig(plot_path)
            generated.append(plot_path)

        # Close all figures
        import matplotlib.pyplot as plt
        if show:
            plt.show()
        plt.close('all')

        # Delete old figures
        for path in glob.glob(os.path.join(pfunk.DIR_PLOT, mask)):
            path = os.path.realpath(path)
            if not path.startswith(pfunk.DIR_PLOT):
                continue
            if path in generated:
                continue
            try:
                os.remove(path)
                log.info('Removed old plot: ' + path)
            except IOError:
                log.info('Removal of old plot failed: ' + path)

    def _run(self, result_writer):
        """
        This will be defined for an individual test. It will run the test,
        store any test results using ``result_writer``.
        Args:

        result_writer -- the test can use this to write any test outputs as
        ``result_writer[output_name] = output_value``

        """
        raise NotImplementedError

    def run(self):
        """
        Runs this test and logs the output.
        """
        # Create logger for _global_ console/file output
        log = logging.getLogger(__name__)
        log.info('Running test: ' + self.name())

        # Seed numpy random generator, so that we know the value
        seed = np.random.randint(2**32)    # Numpy says max seed is 2**32 - 1
        np.random.seed(seed)

        # Create test name
        date = pfunk.date()
        name = self.name()

        # Create result writer

        w = self._writer_generator(name, date)
        w['status'] = 'unitialised'
        w['date'] = date
        w['name'] = name
        w['python'] = pfunk.PYTHON_VERSION
        w['pints'] = pfunk.PINTS_VERSION
        w['pints_commit'] = pfunk.PINTS_COMMIT
        w['pfunk_commit'] = pfunk.PFUNK_COMMIT
        w['commit'] = pfunk.PFUNK_COMMIT + '/' + pfunk.PINTS_COMMIT
        w['seed'] = seed

        # Run test
        try:
            self._run(w)
        except Exception:
            log.error('Exception in test: ' + self.name())
            w['status'] = 'failed'
            raise
        finally:
            log.info('Writing result to ' + w.filename())
            w.write()

