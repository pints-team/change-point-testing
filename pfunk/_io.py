#
# IO module.
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2019, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
from __future__ import absolute_import, division
from __future__ import print_function, unicode_literals

import os
import re
import time
import logging
import numpy as np
from scipy import stats

import pfunk
from ._resultsdb import find_test_dates

# String types in Python 2 and 3
try:
    basestring
except NameError:
    basestring = str


# High-precision floats
FLOAT_FORMAT = '{: .17e}'

# Result key format
RESULT_KEY = re.compile(r'^[a-zA-Z]\w*$')


def unique_path(path):
    """
    Returns a unique path equal or similar to the given one.
    """
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    base += '-'
    i = 2
    while os.path.exists(path):
        path = base + str(i) + ext
        i += 1
    return path


def clean_filename(filename):
    """ Tidies up a filename and returns it. """
    filename = str(filename)  # Separate line for nicer debugging if this fails
    return os.path.abspath(os.path.expanduser(filename))


def find_test_plots():
    """
    Scans the plot directory, and returns a tuple ``(plots, dates)``, where
    ``plots`` maps test names to a list of their most recent plot files, and
    ``dates`` maps test names to the corresponding dates.
    """
    # Get logger
    log = logging.getLogger(__name__)

    # Get a list of available tests
    import pfunk.tests
    names = pfunk.tests.tests()
    plots = {}
    dates = {}

    # Find all plot files
    for path in os.listdir(pfunk.DIR_PLOT):

        # Attempt to read filename as test result
        base, ext = os.path.splitext(path)
        parts = base.split('-', 1)
        if len(parts) != 2:
            log.info('Skipping file in plot dir ' + path)
            continue
        name, date = parts

        # Multiple plots? Then get index
        pos = date.rfind(':')
        pos = date.find('-', pos)
        if pos >= 0:
            #index = int(date[pos + 1:])
            date = date[:pos]

        # Skip unknown tests
        if name not in names:
            continue

        # Attempt to parse date
        date = time.strptime(date, pfunk.DATE_FORMAT)

        # Store plot if latests

        if name not in dates or date > dates[name]:
            dates[name] = date
            plots[name] = [path]
        elif date == dates[name]:
            plots[name].append(path)

    return plots, dates


def find_next_test(database):
    """
    Scans the results directory, and returns the test that hasn't been run for
    the longest.
    """
    dates = find_test_dates(database)
    return min(dates, key=dates.get)


def find_previous_test(database):
    """
    Scans the results directory, and returns the test that has been run most
    recently.
    """
    dates = find_test_dates(database)
    return max(dates, key=dates.get)


def gather_statistics_per_commit(
        results, variable, remove_outliers=False, short_names=True, n=None):
    """
    Gathers mean and standard devations of the given variable on a per commit
    basis.

    Returns a tuple ``(commits, values, unique, mean, std)``, where ``commits``
    is a list of commit names (ordered by date) and ``values`` are the
    corresponding values. Next, ``unique`` is a list of unique commit names,
    and ``mean`` and ``std`` are the mean and standard deviations per unique
    commit.

    Arguments::

    ``results``
        The results object to get data from.
    ``variable``
        The variable to get data for.
    ``remove_outliers``
        Optional argument. If set to ``True`` outliers will be removed from the
        returned data, and won't be included when calculating mean and std.
    ``short_names``
        Optional argument. If set to ``False`` the long commit names will be
        returned.
    ``n``
        Optional argument. If set, only the last n unique commits will be
        analysed

    """
    # Fetch commits and scores
    commits, scores = results['commit', variable]

    # Gather values per commit
    unique = []
    values = []
    lookup = {}
    for i, commit in enumerate(commits):
        # Get appropriate commit list
        try:
            j = lookup[commit]
        except KeyError:
            j = lookup[commit] = len(values)
            values.append([])
            unique.append(commit)

        # Flatten lists (i.e. ess)
        if isinstance(scores[i], (float, int)):
            values[j].append(scores[i])
        else:
            values[j] += list(scores[i])

    # Keep only last n unique commits
    if n is not None:
        unique = unique[-n:]
        values = values[-n:]
        cut_off = 0
        for i, x in enumerate(commits):
            if x not in unique:
                cut_off = i
        commits = commits[cut_off:]
        scores = scores[cut_off:]

    # Convert to short commit names
    def shorten(commit):
        """ Shorten commit names, possibly multiple separated by '/'. """
        return '\n'.join([x.strip()[:7] for x in commit.split('/')])
    if short_names:
        unique = [shorten(x) for x in unique]
        commits = [shorten(x) for x in commits]

    # Remove outliers
    if remove_outliers:
        r = 2
        for i in range(len(values)):
            y = np.array(values[i])
            y = y[np.isfinite(y)]
            if len(y) < 2:
                continue
            #mid, rng = np.mean(y), np.std(y)
            mid, rng = stats.scoreatpercentile(y, 50), stats.iqr(y)
            distance = np.abs(y - mid)
            ifurthest = np.argmax(distance)
            while distance[ifurthest] > r * rng:
                y = np.delete(y, ifurthest)
                #mean, std = np.mean(y), np.std(y)
                mid, rng = stats.scoreatpercentile(y, 50), stats.iqr(y)
                distance = np.abs(y - mid)
                ifurthest = np.argmax(distance)
            values[i] = y

    # Reconstruct commits/scores arrays from filtered data, and collapse
    # multi-valued data if given (e.g ess)
    commits = []
    scores = []
    for i, y in enumerate(values):
        commits.extend([unique[i]] * len(y))
        scores.extend(y)

    # Gather mean and standard deviation
    mean = []
    std = []
    for y in values:
        y = np.array(y)
        yf = y[np.isfinite(y)]
        if len(yf):
            mean.append(np.mean(yf))
            std.append(np.std(yf))
        else:
            mean.append(y[0])
            std.append(0)

    return commits, scores, unique, mean, std


def assert_not_deviated_from(mean, sigma, results, variable):
    """
    Given a normal distribution of likelihood defined by ``mean`` and
    `` sigma``, this returns true if the given variable has not deviated by
    more than 3 sigmas from the mean over the last three commits.
    """
    x, y, u, m, s = gather_statistics_per_commit(
        results, variable, remove_outliers=False)
    return np.allclose(np.array(m[-3:]), mean, atol=3 * sigma)


def generate_report(database):
    """
    Generates a markdown file containing information about all tests, including
    links to the most recent plots.
    """
    # Get a list of available tests and the date they were last run
    dates = find_test_dates(database)

    # Gather the status of every test
    import pfunk.tests
    states = {}
    failed = []
    passed = []
    for key in sorted(dates.keys()):
        result = pfunk.tests.analyse(key, database)
        states[key] = result
        if result:
            passed.append(key)
        else:
            failed.append(key)

    # Get a list of available tests and their most recent plots
    plots, plot_dates = find_test_plots()

    # Friendly date format
    def dfmt(when=None):
        f = '%Y-%m-%d %H:%M:%S'
        return time.strftime(f) if when is None else time.strftime(f, when)

    # Plot location, relative to file
    filename = os.path.join(pfunk.DIR_RES_REPO, 'README.md')
    dirname = os.path.relpath(pfunk.DIR_PLOT, start=pfunk.DIR_RES_REPO)

    # Generate markdown report
    eol = '\n'
    with open(filename, 'w') as f:

        # Header
        f.write('# Pints functional testing report' + 3 * eol)
        f.write('Generated on: ' + dfmt() + 3 * eol)

        # List of failed tests
        if failed:
            f.write('Failed tests:' + eol)
            for name in failed:
                f.write('- [' + name + '](#' + name.lower() + ')' + eol)
        else:
            f.write('All tests passed.' + eol)
        f.write(eol)

        # List of passed tests
        if passed:
            f.write('Passed tests:' + eol)
            for name in passed:
                f.write('- [' + name + '](#' + name.lower() + ')' + eol)
            f.write(eol)

        # Note about axis labels
        f.write('### Note about axis labels' + eol)
        f.write('Labels on the x-axis commonly use the notation ')
        f.write('`<pints commit> <pfunk commit>`.' + eol)
        f.write(eol)

        # Individual tests
        for name, date in sorted(dates.items(), key=lambda x: x[0]):
            f.write('## ' + name + 2 * eol)
            f.write('- Last run on: ' + dfmt(date) + eol)
            f.write('- Status: ' + ('ok' if states[name] else 'FAILED') + eol)

            if name in plots:
                f.write(
                    '- Last plots generated on: ' + dfmt(plot_dates[name])
                    + eol)
                for plot in sorted(
                        plots[name], key=lambda x: os.path.splitext(x)[0]):
                    path = os.path.join(dirname, plot)
                    f.write(eol + '![' + plot + '](' + path + ')' + eol)
                f.write(eol)

            f.write(eol)

    # Generate badge
    generate_badge(len(failed) > 0)


def generate_badge(failed=False):
    """
    Generates a badge for github.
    """
    # Plot location, relative to file
    filename = os.path.join(pfunk.DIR_RES_REPO, 'badge.svg')

    badge = []
    badge.append(
        '<svg xmlns="http://www.w3.org/2000/svg"'
        ' xmlns:xlink="http://www.w3.org/1999/xlink"'
        ' width="88" height="20">')
    badge.append(
        '<linearGradient id="b" x2="0" y2="100%">'
        '<stop offset="0" stop-color="#bbb" stop-opacity=".1"/>'
        '<stop offset="1" stop-opacity=".1"/>'
        '</linearGradient>'
    )
    badge.append(
        '<clipPath id="a">'
        '<rect width="88" height="20" rx="3" fill="#fff"/>'
        '</clipPath>'
    )
    #colour = '#e05d44' if failed else '#4c1'
    colour = '#2a88d0'

    badge.append(
        '<g clip-path="url(#a)">'
        '<path fill="#555" d="M0 0h37v20H0z"/>'
        '<path fill="' + colour + '" d="M37 0h51v20H37z"/>'
        '<path fill="url(#b)" d="M0 0h88v20H0z"/>'
        '</g>'
    )
    badge.append(
        '<g fill="#fff" text-anchor="middle"'
        ' font-family="DejaVu Sans,Verdana,Geneva,sans-serif"'
        ' font-size="110">'
    )

    title = 'pfunk'
    badge.append(
        '<text x="195" y="150" transform="scale(.1)"'
        ' fill="#010101" fill-opacity=".3"'
        ' textLength="270">' + title + '</text>'
    )
    badge.append(
        '<text x="195" y="140" transform="scale(.1)"'
        ' textLength="270">' + title + '</text>'
    )

    #pass_text = 'failing' if failed else 'passing'
    #pass_text_length = str(330 if failed else 410)
    pass_text = 'running'
    pass_text_length = str(410)

    badge.append(
        '<text x="615" y="150" transform="scale(.1)"'
        ' fill="#010101" fill-opacity=".3"'
        ' textLength="' + pass_text_length + '">' + pass_text + '</text>'
    )
    badge.append(
        '<text x="615" y="140" transform="scale(.1)"'
        ' textLength="' + pass_text_length + '">' + pass_text + '</text>'
    )
    badge.append('</g>')
    badge.append('</svg>')

    with open(filename, 'w') as f:
        f.write(''.join(badge))

