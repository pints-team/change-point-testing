#
# Shared plotting code.
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2019, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
from __future__ import absolute_import, division
from __future__ import print_function, unicode_literals

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import pfunk


def histogram(results, variable, title, xlabel, threshold=None):
    """
    Creates and returns a histogram plot for a variable (over commits).
    """
    fig = plt.figure(figsize=(11, 4.5))
    plt.suptitle(title + ' : ' + pfunk.date())

    # Left plot: Variable per commit for all data as 1 histogram
    plt.subplot(1, 2, 1)
    fig.autofmt_xdate()
    x, y, u, m, s = pfunk.gather_statistics_per_commit(results, variable)
    if len(x) == 0:
        plt.text(0.5, 0.5, 'No data')
    else:
        y = np.asarray(y)
        last_commit = [i for i, k in enumerate(x) if k == u[-1]]
        mask_lc = np.ones(y.shape, dtype=bool)
        mask_lc[last_commit] = False

        n, _, _ = plt.hist(y[mask_lc], bins='auto', color='#607c8e', alpha=0.7,
                label='All %s commits' % len(u))

        if len(last_commit) > 25:
            plt.hist(y[last_commit], bins='auto', color='#0504aa', alpha=0.5,
                    label='Last commit')
        else:
            stem_height = [np.max(n)] * len(last_commit)
            ml, sl, bl = plt.stem(y[last_commit], stem_height,
                    label='Last commit')
            plt.setp(ml, color='#0504aa', alpha=0.5)
            plt.setp(sl, color='#0504aa', alpha=0.5)
            plt.setp(bl, visible=False)
    plt.ylabel('Frequency (total %s runs)' % len(y))
    plt.xlabel(xlabel)
    plt.legend()

    # Right plot: Same, to most recent data.
    plt.subplot(1, 2, 2)
    n_commits = 12
    fig.autofmt_xdate()
    x, y, u, m, s = pfunk.gather_statistics_per_commit(results, variable,
            n=n_commits)
    if len(x) == 0:
        plt.text(0.5, 0.5, 'No data')
    else:
        y = np.asarray(y)
        last_commit = [i for i, k in enumerate(x) if k == u[-1]]
        mask_lc = np.ones(y.shape, dtype=bool)
        mask_lc[last_commit] = False
        
        n, _, _ = plt.hist(y[mask_lc], bins='auto', color='#607c8e', alpha=0.7,
                label='Last %s commits' % n_commits)

        if len(last_commit) > 10:
            plt.hist(y[last_commit], bins='auto', color='#0504aa', alpha=0.5,
                    label='Last commit')
        else:
            stem_height = [np.max(n)] * len(last_commit)
            ml, sl, bl = plt.stem(y[last_commit], stem_height,
                    label='Last commit')
            plt.setp(ml, color='#0504aa', alpha=0.5)
            plt.setp(sl, color='#0504aa', alpha=0.5)
            plt.setp(bl, visible=False)
    plt.ylabel('Frequency (total %s runs)' % len(y))
    plt.xlabel(xlabel)
    plt.legend()
        
    return fig


def variable(results, variable, title, ylabel, threshold=None):
    """
    Creates and returns a default plot for a variable vs commits.
    """
    fig = plt.figure(figsize=(11, 4.5))
    plt.suptitle(title + ' : ' + pfunk.date())

    r = 0.3

    # Left plot: Variable per commit, all data
    plt.subplot(1, 2, 1)
    plt.ylabel(ylabel)
    plt.xlabel('Commit')
    fig.autofmt_xdate()
    x, y, u, m, s = pfunk.gather_statistics_per_commit(results, variable)
    if len(x) == 0:
        plt.text(0.5, 0.5, 'No data')
    else:
        xlookup = dict(zip(u, np.arange(len(u))))
        x = np.array([xlookup[i] for i in x], dtype=float)
        x += np.random.uniform(-r, r, x.shape)
        plt.plot(u, m, 'ko-', alpha=0.5)
        plt.plot(x, y, 'x', alpha=0.75)
        if threshold:
            plt.axhline(threshold)
        try:
            y = np.array(y)
            ymax = np.max(y[np.isfinite(y)])
        except ValueError:
            ymax = 1

    # Right plot: Same, but with outliers removed, to achieve a "zoom" on the
    # most common, recent data.
    plt.subplot(1, 2, 2)
    plt.ylabel(ylabel)
    plt.xlabel('Commit')
    fig.autofmt_xdate()
    x, y, u, m, s = pfunk.gather_statistics_per_commit(
        results, variable, remove_outliers=True, n=10)
    if len(x) == 0:
        plt.text(0.5, 0.5, 'No data')
    else:
        xlookup = dict(zip(u, np.arange(len(u))))
        x = np.array([xlookup[i] for i in x], dtype=float)
        x += np.random.uniform(-r, r, x.shape)
        plt.plot(u, m, 'ko-', alpha=0.5)
        plt.plot(x, y, 'x', alpha=0.75)
        if threshold:
            # Show threshold line only if it doesn't change the zoom
            if threshold <= np.max(y) and threshold >= np.min(y):
                plt.axhline(threshold)
        y = np.array(y)
        try:
            y = np.array(y)
            ymax = max(ymax, np.max(y[np.isfinite(y)]))
        except ValueError:
            pass

        if ymax > 1000:
            plt.subplots_adjust(0.1, 0.16, 0.99, 0.92, 0.2, 0)
        else:
            plt.subplots_adjust(0.07, 0.16, 0.99, 0.92, 0.17, 0)

    return fig


def convergence(results, xvar, yvar, title, xlabel, ylabel, ymin, ymax):
    """
    Plots a variable over e.g. time, iterations, evaluations.
    """
    fig = plt.figure(figsize=(11, 4.5))
    plt.suptitle(title + ' (' + pfunk.date() + ')')

    xs, ys = results[xvar, yvar]
    if len(xs) == 0:
        plt.text(0.5, 0.5, 'No data')
        return fig

    # Left plot: All data, full view
    plt.subplot(1, 2, 1)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    for i, x in enumerate(xs):
        plt.plot(x, ys[i])

    # Right plot: Same data, but zoomed in
    plt.subplot(1, 2, 2)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    for i, x in enumerate(xs):
        plt.plot(x, ys[i])
    ymin = max(ymin, min([np.min(y) for y in ys]))
    ymax = min(ymax, max([np.max(y) for y in ys]))
    plt.ylim(ymin, ymax)

    if ymax > 1000 or ymax < 1.5:
        plt.subplots_adjust(0.1, 0.1, 0.99, 0.92, 0.2, 0)
    else:
        plt.subplots_adjust(0.07, 0.1, 0.99, 0.92, 0.15, 0)

    return fig
