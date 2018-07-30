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
    base, ext = path.splitext()
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
            # Lists: Only lists of floats are supported
            value = np.array(value, dtype=float)

        # Store string representation
        if isinstance(value, int):
            self._data[key] = str(value)
        elif isinstance(value, float):
            self._data[key] = FLOAT_FORMAT.format(value)
        elif isinstance(value, list):
            self._data[key] = (
                + '['
                + ', '.join([FLOAT_FORMAT.format(x) for x in value])
                + ']'
            )
        elif isinstance(value, np.ndarray):
            if value.ndim > 1:
                raise ValueError(
                    'Unable to store arrays of 2 or more dimensions.')
            self._data[key] = (
                '[' + ', '.join([FLOAT_FORMAT.format(x) for x in value]) + ']')
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

                    value = value[1:-1].split(',')
                    try:
                        return np.array([float(x) for x in value])
                    except ValueError:
                        log.error(
                            'Unable to parse array for ' + key + ' on line '
                            + str(1 + k) + ' of ' + self._filename)
                        continue

                elif value[:1] == '"':
                    # String

                    value = value[1:-1]

                elif '.' in value:
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
        date = time.strptime(date, pfunk.DATE_FORMAT)
        last = dates[name]
        if last is None or date > last:
            dates[name] = date

    return dates


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

