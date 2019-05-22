#
# Lists all tests.
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2019, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
import os

import glob
import logging
import numpy as np
import pfunk


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

    def analyse(self, database):
        """
        Checks if the test passed or failed

        At the moment this just prints if the test has passed or failed. This
        should do something more intelligent, e.g. email someone
        """

        # Create logger for _global_ console/file output
        log = logging.getLogger(__name__)
        log.info('Running analyse: ' + self.name())

        # Load test results
        results = pfunk.find_test_results(self._name, database)

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

    def plot(self, database, show=False):
        """
        Generates the plots defined for this test

        All plots returned by the test are written out to a filename defined
        by the test name. If ``show==True`` then the figures are also shown on
        the current display.
        """
        # Create logger for _global_ console/file output
        log = logging.getLogger(__name__)
        log.info('Running plot: ' + self.name())

        # Load test results
        results = pfunk.find_test_results(self._name, database)

        # Plot
        try:
            figs = self._plot(results)
        except Exception:
            log.error('Exception in plot: ' + self.name())
            raise

        # Ensure the plots directory exists, or script will fail on fig.savefig
        os.makedirs(pfunk.DIR_PLOT, exist_ok=True)

        # Path for single figure (will be adapted if there's more)
        path = self.name() + '.svg'

        # Delete existing files
        generated = []
        mask = self.name() + '*.svg'
        # Delete old figures
        for path in glob.glob(os.path.join(pfunk.DIR_PLOT, mask)):
            path = os.path.realpath(path)
            if not path.startswith(pfunk.DIR_PLOT):
                break
            try:
                os.remove(path)
                log.info('Removed old plot: ' + path)
            except IOError:
                log.info('Removal of old plot failed: ' + path)

        # Store
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

    def _run(self, result_writer):
        """
        This will be defined for an individual test. It will run the test,
        store any test results using ``result_writer``.
        Args:

        result_writer -- the test can use this to write any test outputs as
        ``result_writer[output_name] = output_value``

        """
        raise NotImplementedError

    def run(self, path, run_number):
        """
        Runs this test and logs the output.
        """
        # Log status
        log = logging.getLogger(__name__)
        log.info(f'Running test: {self._name} run {run_number}')

        # Seed numpy random generator, so that we know the value
        max_uint32 = np.iinfo(np.uint32).max
        seed = int(np.mod(np.random.randint(max_uint32) + run_number, max_uint32))
        np.random.seed(seed)

        # Create test name
        date = pfunk.date()
        name = self.name()

        # Store an identifier to the result writer's output, so we don't have to hold onto it
        # while running the (potentially very long) test
        results_id = None

        # Create result writer
        with self._writer_generator(name, date, path) as w:
            w['status'] = 'uninitialised'
            w['date'] = date
            w['name'] = name
            w['python'] = pfunk.PYTHON_VERSION
            w['pints'] = pfunk.PINTS_VERSION
            w['pints_commit'] = pfunk.PINTS_COMMIT
            w['pints_authored_date'] = pfunk.PINTS_COMMIT_AUTHORED
            w['pints_committed_date'] = pfunk.PINTS_COMMIT_COMMITTED
            w['pints_commit_msg'] = pfunk.PINTS_COMMIT_MESSAGE
            w['pfunk_commit'] = pfunk.PFUNK_COMMIT
            w['pfunk_authored_date'] = pfunk.PFUNK_COMMIT_AUTHORED
            w['pfunk_committed_date'] = pfunk.PFUNK_COMMIT_COMMITTED
            w['pfunk_commit_msg'] = pfunk.PFUNK_COMMIT_MESSAGE
            w['seed'] = seed
            results_id = w.row_id()

        # Run test
        results = {}
        try:
            self._run(results)
        except Exception:
            log.error('Exception in test: ' + self.name())
            results['status'] = 'failed'
            raise
        finally:
            log.info('Writing result to ' + path)
            with self._writer_generator(name, date, path, results_id) as w:
                for k in results.keys():
                    w[k] = results[k]
