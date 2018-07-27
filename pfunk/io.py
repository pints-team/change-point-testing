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

# StringIO in Python 2 and 3
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


# High-precision floats
FLOAT_FORMAT = '{: .17e}'

# Result key format
RESULT_KEY = re.compile(r'^[a-zA-Z]\w*$')


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
            if value.ndims > 1:
                raise ValueError(
                    'Unable to store arrays of 2 or more dimensions.')
            self._data[key] = (
                + '['
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
        dates[name] = None

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















#
