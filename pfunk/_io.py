#
# IO module.
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2018, University of Oxford.
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


def can_write_file(filename, allow_overwrite=False):
    """ Checks if we can write to the given filename. """
    # Check if path exists
    if os.path.exists(filename):
        if not allow_overwrite:
            return False
        # Explicitly exclude links and directories
        if os.path.islink(filename) or os.path.isdir(filename):
            return False
        # Check for write access
        return os.access(filename, os.W_OK)

    # Check parent directory is writable
    return os.access(os.path.dirname(filename) or '.', os.W_OK)


class ResultWriter(object):
    """
    Writes results (key-value pairs) to file.

    Example:

        w = ResultWriter('test.txt')
        w['test'] = 123
        w.write()

    """

    def __init__(self, filename, overwrite=False):
        filename = clean_filename(filename)
        if not can_write_file(filename, allow_overwrite=overwrite):
            raise ValueError('Unable to write to ' + filename)
        self._filename = filename

        # Key-value pairs (both string)
        self._data = {}

    def __setitem__(self, key, value):
        """
        Stores a name / value pair for later writing.
        """
        key = str(key)
        if RESULT_KEY.match(key) is None:
            raise ValueError('Invalid key: ' + key)

        # Conversions
        if isinstance(value, list):
            value = np.array(value)

        # Store string representation
        if isinstance(value, int):
            self._data[key] = str(value)
        elif isinstance(value, float):
            self._data[key] = FLOAT_FORMAT.format(value)
        elif isinstance(value, np.ndarray):
            if value.ndim > 1:
                raise ValueError(
                    'Unable to store arrays of 2 or more dimensions.')
            if value.dtype == int:
                self._data[key] = (
                    '[' + ', '.join([str(x) for x in value]) + ']')
            else:
                self._data[key] = (
                    '['
                    + ', '.join([FLOAT_FORMAT.format(x) for x in value])
                    + ']'
                )
        elif isinstance(value, basestring):
            # Check for newlines
            if '\n' in value or '\r' in value:
                raise ValueError('Multi-line strings are not supported.')
                self._data[key] = value
            # Store, wrapped in quotes (don't bother escaping)
            self._data[key] = '"' + value + '"'
        else:
            raise ValueError(
                'Unsupported data type ' + str(type(value)) + ' for ' + key)

    def set(self, **kwargs):
        """
        Sets mutliple values, using the syntax ``set(x=5, y=6)``.
        """
        for k, v in kwargs:
            self[k] = v

    def write(self):
        """ Writes this result to file. """
        with open(self._filename, 'w') as f:
            f.write(str(self) + '\n')

    def __str__(self):
        return '\n'.join([k + ': ' + v for k, v in sorted(self._data.items())])

    def filename(self):
        """ Returns this ResultWriter's filename. """
        return self._filename


class ResultReader(object):
    """
    Reads a results file, providing access to its key-value pair data.
    """

    def __init__(self, filename):
        self._filename = clean_filename(filename)

        # Key-value pairs (both string)
        self._data = {}

        # Read!
        self._parse()

    def __getitem__(self, key):
        # Note contents of complex type e.g. array can be modified by user
        return self._data[key]

    def __contains__(self, key):
        return key in self._data

    def __len__(self):
        return len(self._data)

    def _parse(self):
        """ Reads the data file, stores the key-value pairs. """
        # Get logger
        log = logging.getLogger(__name__)

        # Parse file
        with open(self._filename, 'r') as f:
            for k, line in enumerate(f):

                # Ignore empty lines
                line = line.strip()
                if not line:
                    continue

                # Split key and value
                try:
                    i = line.index(':')
                except ValueError:
                    log.error(
                        'Unable to parse line ' + str(1 + k) + ' of '
                        + self._filename)
                    continue

                # Test key
                key = line[:i]
                if RESULT_KEY.match(key) is None:
                    log.error(
                        'Invalid key "' + key + '" on line ' + str(1 + k)
                        + ' of ' + self._filename)
                    continue

                # Parse value
                value = line[i + 1:].strip()

                if value[:1] == '[':
                    # Array

                    floats = '.' in value or 'nan' in value or 'inf' in value
                    value = value[1:-1].split(',')
                    try:
                        if floats:
                            value = np.array([float(x) for x in value])
                        else:
                            value = np.array([int(x) for x in value])
                    except ValueError:
                        log.error(
                            'Unable to parse array for ' + key + ' on line '
                            + str(1 + k) + ' of ' + self._filename)
                        continue

                elif value[:1] == '"':
                    # String

                    value = value[1:-1]

                elif '.' in value or 'nan' in value or 'inf' in value:
                    # Float

                    try:
                        value = float(value)
                    except ValueError:
                        log.error(
                            'Unable to parse float for ' + key + ' on line '
                            + str(1 + k) + ' of ' + self._filename)
                        continue

                else:
                    # Int

                    try:
                        value = int(value)
                    except ValueError:
                        log.error(
                            'Unable to parse int for ' + key + ' on line '
                            + str(1 + k) + ' of ' + self._filename)
                        continue

                # Store
                self._data[key] = value

    def __str__(self):
        return '\n'.join(
            [k + ': ' + str(v) for k, v in sorted(self._data.items())])


class ResultSet(object):
    """
    Container for ResultReaders for the same test.

    Data can be obtained from a ResultSet using::

        x = ResultSet(result_files)
        scores = x['score']

    This will return scores for all result files that have a ``score`` field
    set.

    Similarly, use::

        dates, commits, scores = x['date', 'commit', 'score']

    to get data from all files where ``date``, ``commit``, and ``score`` are
    all set.
    """

    def __init__(self, result_files):
        self._result_files = result_files
        self._result_files.sort()

        self._result_readers = None
        self._cached = {}

    def _read(self):
        """ Reads all result files. """
        self._result_readers = [ResultReader(x) for x in self._result_files]

    def __getitem__(self, key):

        try:
            # Attempt to use cached version
            return self._cached[key]

        except KeyError:

            # Read result files if not yet done
            if self._result_readers is None:
                self._read()

            # Treat single-value case like multi-value case
            single_value = (type(key) != tuple)
            if single_value:
                key = (key, )

            # Gather data
            values = []
            for k in key:
                values.append([])
            for reader in self._result_readers:
                try:
                    row = [reader[k] for k in key]
                except KeyError:
                    continue
                for k, value in enumerate(values):
                    value.append(row[k])

            # Cache data and return
            self._cached[key] = values
            return values[0] if single_value else values


def find_test_dates():
    """
    Scans the results directory, and returns a dict mapping test names to the
    time (a ``time.struct_time``) when they were last run.
    """
    # Get logger
    log = logging.getLogger(__name__)

    # Get a list of available tests and the date they were last run
    import pfunk.tests
    dates = {}
    for name in pfunk.tests.tests():
        dates[name] = time.struct_time([0] * 9)

    # Find all result files
    for path in os.listdir(pfunk.DIR_RESULT):

        # Attempt to read filename as test result
        base, ext = os.path.splitext(path)
        parts = base.split('-', 1)
        if len(parts) != 2:
            log.info('Skipping file in results dir ' + path)
            continue
        name, date = parts

        # Skip unknown tests
        if name not in dates:
            continue

        # Attempt to parse date
        # remember to clean off trailing '-2.txt' if there
        cleaned_to_date_format = re.sub(r'''-[0-9]+$''', '', date)
        date = time.strptime(cleaned_to_date_format, pfunk.DATE_FORMAT)
        last = dates[name]
        if last is None or date > last:
            dates[name] = date

    return dates


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


def find_next_test():
    """
    Scans the results directory, and returns the test that hasn't been run for
    the longest.
    """
    dates = find_test_dates()
    return min(dates, key=dates.get)


def find_test_results(test_name):
    """
    Returns a ResultSet for the given ``test_name``.
    """
    # Find all result files
    results = []
    for path in os.listdir(pfunk.DIR_RESULT):

        # Attempt to read filename as test result
        base, ext = os.path.splitext(path)
        parts = base.split('-', 1)
        if len(parts) != 2:
            continue
        name, date = parts

        # Skip other tests
        if name == test_name:
            results.append(os.path.join(pfunk.DIR_RESULT, path))

    return ResultSet(results)


def gather_statistics_per_commit(
        results, variable, remove_outliers=False, short_names=True):
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


def generate_report():
    """
    Generates a markdown file containing information about all tests, including
    links to the most recent plots.
    """
    # Get a list of available tests and the date they were last run
    dates = find_test_dates()

    # Gather the status of every test
    import pfunk.tests
    states = {}
    failed = []
    passed = []
    for key in sorted(dates.keys()):
        result = pfunk.tests.analyse(key)
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
    colour = '#e05d44' if failed else '#4c1'
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

    pass_text = 'failing' if failed else 'passing'
    pass_text_length = str(330 if failed else 410)
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

