#
# Nested sampling test: Can we recover a twisted gaussian banana distribution?
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2019, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
import logging

import pfunk


class NestedBanana(pfunk.FunctionalTest):
    """
    Runs a NestedSampling algorithm on a twisted gaussian banana LogPDF. Stores
    the Kullback-Leibler divergence between the result and the true solution.

    Arguments:

    ``writer_generator``
        A callable that will return a key-value store for test results.
    ``method``
        A *string* indicating the method to use, e.g. 'NestedEllipsoidSampler'.
        (Must be a string, because we shouldn't import pints before we start
        testing.)

    """

    def __init__(self, writer_generator, method, pass_threshold):

        # Can't check method here, don't want to import pints
        self._method = str(method)
        self._pass_threshold = float(pass_threshold)

        # Create name and initialise
        name = 'nested_banana_' + self._method
        super(NestedBanana, self).__init__(name, writer_generator)

    def _run(self, result):

        import pints
        import pints.toy

        # Allow slightly older pints versions to be tested
        try:
            from pints.toy import TwistedGaussianLogPDF
        except ImportError:
            from pints.toy import TwistedNormalLogPDF as TwistedGaussianLogPDF
        try:
            from pints import MultivariateGaussianLogPrior
        except ImportError:
            from pints import MultivariateNormalLogPrior \
                as MultivariateGaussianLogPrior

        log = logging.getLogger(__name__)

        DEBUG = False

        # Show method name
        log.info('Using method: ' + self._method)

        # Get method class
        method = getattr(pints, self._method)

        # Create a log pdf (use multi-modal, but with a single mode)
        log_pdf = TwistedGaussianLogPDF(dimension=2, b=0.1)

        # Create a log prior
        log_prior = MultivariateGaussianLogPrior(
            [0, 0], [[10, 0], [0, 10]])

        # Create a nested sampler
        sampler = method(log_pdf, log_prior)

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
            'Banana w. ' + self._method,
            'Kullback-Leibler divergence', 3 * self._pass_threshold)
        )

        return figs
