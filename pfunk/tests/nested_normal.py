#
# Simplest nested sampling test: Can we recover a unimodal normal distribution?
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2019, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
import pfunk


class NestedNormal(pfunk.FunctionalTest):
    """
    Runs a NestedSampling algorithm on a normal LogPDF. Stores the distance of
    the resulting mean to the true solution.

    Arguments:

    ``writer_generator``
        A callable that will return a key-value store for test results.
    ``method``
        A *string* indicating the method to use, e.g. 'AdaptiveCovarianceMCMC'.
        (Must be a string, because we shouldn't import pints before we start
        testing.)

    """

    def __init__(self, writer_generator, method, pass_threshold):

        # Can't check method here, don't want to import pints
        self._method = str(method)
        self._pass_threshold = float(pass_threshold)

        # Create name and initialise
        name = 'nested_normal_' + self._method
        super(NestedNormal, self).__init__(name, writer_generator)

    def _run(self, result):

        import pints
        import pints.toy
        import numpy as np

        import logging
        log = logging.getLogger(__name__)

        DEBUG = False

        # Show method name
        log.info('Using method: ' + self._method)

        # Get method class
        method = getattr(pints, self._method)

        # Create a log pdf
        xtrue = np.array([2, 4])
        sigma = np.diag(np.array([1, 3]))
        log_pdf = pints.toy.GaussianLogPDF(xtrue, sigma)

        # Create a log prior
        log_prior = pints.MultivariateGaussianLogPrior(xtrue + 1, sigma * 2)

        # Create a nested sampler
        sampler = pints.NestedController(log_pdf, log_prior, method=method)

        # Log to file
        if not DEBUG:
            sampler.set_log_to_screen(False)

        # Set max iterations
        sampler.set_iterations(4000)
        sampler.set_posterior_samples(1000)

        # Run
        samples, logZ = sampler.run()

        # Store kullback-leibler divergence
        result['kld'] = log_pdf.kl_divergence(samples)

        # Store status
        result['status'] = 'done'

    def _analyse(self, results):
        return pfunk.assert_not_deviated_from(
            0, self._pass_threshold, results, 'kld')

    def _plot(self, results):

        figs = []

        # Figure: KL per commit
        figs.append(pfunk.plot.variable(
            results,
            'kld',
            'Normal w. ' + self._method,
            'Kullback-Leibler divergence', 3 * self._pass_threshold)
        )
        figs.append(pfunk.ChangePints().data(results['kld']).figure())

        return figs
