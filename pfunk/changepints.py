#
# Changepoint detection
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2019, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
import numpy as np
import ruptures as rpt

class ChangePints:
    """
    Methods for changepoint detection
    """

    def __init__(self, model="rbf", penalty=3):
        """
        Creates ChangePints object

        :param model: model (default rbf)to use, same as options in ruptures.detection.Pelt
        :param penalty: penalty, same option as ruptures.detection.Pelt.predict
        """
        self.model = model
        self.penalty = penalty

    def data(self, source):
        """
        Loads data from source and performs changepoint detection

        :param source: timeseries array
        """
        self.signal = np.array(source).flatten()
        algo = rpt.Pelt(model=self.model).fit(self.signal)
        self.bkpts = algo.predict(pen=self.penalty)
        return self

    def breakpoints(self):
        """
        Returns list of breakpoints
        """
        return self.bkpts

    def crossed_threshold(self, nbkpts=1):
        """
        Returns whether threshold of number of breakpoints has been crossed.
        This method is the inverse of :meth:`pfunk.changepints.within_threshold`.

        :param nbkpts: threshold number of breakpoints (default: 1)
        :rtype: bool
        """
        return len(self.breakpoints()) > nbkpts

    def within_threshold(self, nbkpts=1):
        """
        Returns whether number of breakpoints is within threshold.
        This method is the inverse of :meth:`pfunk.changepints.crossed_threshold`.

        :param nbkpts: threshold number of breakpoints (default: 1)
        :rtype: bool
        """
        return not self.crossed_threshold(nbkpts)

    def figure(self):
        """
        Returns figure showing changepoints

        :rtype: :class:`matplotlib.figure.Figure`
        """
        fig, ax = rpt.display(self.signal, self.breakpoints())
        return fig
