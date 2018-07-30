#
# Fake plot for fake test 2
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2018, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
from __future__ import absolute_import, division
from __future__ import print_function, unicode_literals

import matplotlib.pyplot as plt

import pfunk


class Test2Plot(pfunk.SingleTestPlot):

    def __init__(self):
        super(Test2Plot, self).__init__('test2_plot', 'test2')

    def _plot(self, results, plot_path):

        x, y = results['y']

        plt.figure()
        plt.xlabel('Index')
        plt.ylabel('Y')
        plt.plot(y)
        plt.savefig(plot_path)
