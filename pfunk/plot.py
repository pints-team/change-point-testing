#
# Shared plotting code.
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2018, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
from __future__ import absolute_import, division
from __future__ import print_function, unicode_literals

import os
import logging
import numpy as np
import matplotlib.pyplot as plt

import pfunk

def variable(results, variable, title, ylabel):
    """
    Creates and returns a default plot for a variable vs commits.
    """
    fig = plt.figure(figsize=(12, 5))
    plt.suptitle(title + ' : ' + pfunk.date())

    r = 0.3

    plt.subplot(1, 2, 1)
    plt.ylabel(ylabel)
    plt.xlabel('Commit')
    fig.autofmt_xdate()
    x, y, u, m, s = pfunk.gather_statistics_per_commit(results, variable)
    xlookup = dict(zip(u, np.arange(len(u))))
    x = np.array([xlookup[i] for i in x], dtype=float)
    x += np.random.uniform(-r, r, x.shape)
    plt.plot(u, m, 'ks-', alpha=0.25)
    plt.plot(x, y, 'x', alpha=0.5)

    plt.subplot(1, 2, 2)
    plt.ylabel(ylabel)
    plt.xlabel('Commit')
    fig.autofmt_xdate()
    x, y, u, m, s = pfunk.gather_statistics_per_commit(
        results, variable, remove_outliers=True)
    x = np.array([xlookup[i] for i in x], dtype=float)
    x += np.random.uniform(-r, r, x.shape)
    plt.plot(u, m, 'ks-', alpha=0.25)
    plt.plot(x, y, 'x', alpha=0.5)

    return fig
