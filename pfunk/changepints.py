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
import matplotlib.pyplot as plt

class ChangePints:

    def __init__(self, model="rbf", penalty=3):
        self.model = model
        self.penalty = penalty

    def data(self, source):
        self.signal = np.array(source).flatten()
        algo = rpt.Pelt(model=self.model).fit(self.signal)
        self.bkpts = algo.predict(pen=self.penalty)
        return self

    def breakpoints(self):
        return self.bkpts

    def crossed_threshold(self, nbkpts=1):
        "If number of breakpoints > nbkpts, return False"
        return len(self.breakpoints()) > nbkpts

    def show(self):
        rpt.display(self.signal, self.breakpoints())
        plt.show()
