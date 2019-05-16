#
# Results DB module.
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2019, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#

from collections import defaultdict
import json
import sqlite3
import time

import pfunk


def _ensure_database_schema(connection):
    """
    Given a connection to a sqlite3 database, create a table (if needed)
    containing the appropriate columns for our test results.
    """
    query = """ create table if not exists test_results(
    identifier integer primary key asc,
    name varchar,
    date date,
    status varchar,
    python varchar,
    pints varchar,
    pints_commit varchar,
    pfunk_commit varchar,
    commit_hashes varchar,
    pints_authored_date date,
    pints_committed_date date,
    pints_commit_msg varchar,
    pfunk_authored_date date,
    pfunk_committed_date date,
    pfunk_commit_msg varchar,
    seed_1 integer,
    seed_2 integer,
    json varchar
    )"""
    connection.execute(query)
    connection.commit()


class ResultsDatabaseSchemaClient(object):
    """
    Abstract parent for database readers and writers, keeping track of the
    database columns and how to interpret the JSON column.
    """
    primary_columns = ['identifier']
    mapped_columns = {'commit': 'commit_hashes'}
    columns = [
        'name',
        'date',
        'status',
        'python',
        'pints',
        'pints_commit',
        'pfunk_commit',
        'commit_hashes',
        'pints_authored_date',
        'pints_committed_date',
        'pints_commit_msg',
        'pfunk_authored_date',
        'pfunk_committed_date',
        'pfunk_commit_msg',
        'seed_1',
        'seed_2',
    ]

    def json_values(self):
        """
        Interpret the json column in the test results table as a dictionary and
        return it.
        :return: The dictionary retrieved from the json, or the empty dict if
        the field is empty.
        """
        result = self._connection.execute(
            'select json from test_results where identifier = ?', [self._row])
        json_field = result.fetchone()[0]
        dictionary = {}
        if json_field is not None:
            dictionary = json.loads(json_field)
        return dictionary


class ResultsDatabaseWriter(ResultsDatabaseSchemaClient):
    """
    Provides write access to a SQLite3 database containing test results.
    For compatibility with the interfaces supplied by
    ResultsWriter/ResultsReader, the flat-file equivalents, instances of this
    class accept a test name and date, and provide access to the values in a
    row matching. However, due to adding multiprocessing support, test name
    and date no longer uniquely identify a test invocation so a separate
    integer counter is used as the primary key.

    This class is a Context Manager, so use it in a with block:

    >>> with ResultsDatabaseWriter(":memory:", "a_test_name", "2019-01-01T12:34:56") as w:
    ...     w[status] = "pending"
    """

    def __init__(self, filename, test_name, date, existing_row_id=None):
        self._connection = None
        self._filename = filename
        self.__ensure_schema()
        self._name = test_name
        self._date = date
        if existing_row_id is not None:
            self._row = existing_row_id
        else:
            self.__ensure_row_exists()

    def __enter__(self):
        self._connection = connect_to_database(self.filename())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._connection.close()

    def __ensure_schema(self):
        """
        Establish that a test_results table exists, and if it didn't before,
        that it has the correct schema. Note that this method uses a temporary
        connection so it can be called outside the Context Manager lifecycle.
        :return: None.
        """
        conn = connect_to_database(self.filename())
        _ensure_database_schema(conn)
        conn.commit()
        conn.close()

    def __ensure_row_exists(self):
        """
        Create a row in the table to represent the current result, and store
        its primary key.
        Note that this method uses a temporary connection so it can be called outside of the
        Context Manager lifecycle.
        :return: None
        """
        # ensure the row exists
        conn = connect_to_database(self.filename())
        conn.execute(
            'insert into test_results(name,date) values (?,?)',
            (self._name, self._date))
        row_id = conn.execute('select last_insert_rowid()')
        self._row = row_id.fetchone()[0]
        conn.commit()
        conn.close()

    def row_id(self):
        """
        Return the primary key for this writer's table row. Mostly for debugging.
        """
        return self._row

    def __setitem__(self, key, value):
        if key in self.primary_columns:
            # don't update these
            pass
        elif key in self.mapped_columns.keys():
            self[self.mapped_columns[key]] = value
        elif key in self.columns:
            self._connection.execute(
                f'update test_results set {key} = ? where identifier = ?',
                (value, self._row))
            self._connection.commit()
        else:
            dictionary = self.json_values()
            # workaround: if we're given a numpy array, make a Python list
            if getattr(value, 'tolist', None) is not None:
                value = value.tolist()
            dictionary[key] = value
            json_field = json.dumps(dictionary)
            self._connection.execute(
                'update test_results set json = ? where identifier = ?',
                (json_field, self._row))
            self._connection.commit()

    def write(self):
        """
        Provides compatibility with the file-writer interface for writing test
        results.
        :return: None.
        """
        pass

    def filename(self):
        """
        Provides compatibility with the file-writer interface for writing test
        results.
        :return: The path to the database.
        """
        return self._filename


class ResultsDatabaseReader(ResultsDatabaseSchemaClient):
    """
    Provides read access to a row in the test results database.
    """
    def __init__(self, connection, row_id):
        self._connection = connection
        self._row = row_id

    def __getitem__(self, item):
        if item in self.primary_columns or item in self.columns:
            result = self._connection.execute(
                f'select {item} from test_results where identifier = ?',
                [self._row])
            database_row = result.fetchone()
            if database_row is None:
                raise KeyError(
                    f'row_id {self._row} is not present in the database')
            return database_row[0]
        if item in self.mapped_columns.keys():
            return self[self.mapped_columns[item]]
        dictionary = defaultdict(lambda: None, self.json_values())
        return dictionary[item]


class ResultsDatabaseResultsSet(object):
    """
    Represents a collection of rows in the test results database. Provides
    keyed access to the fields in the results, so set['foo'] gives you a list
    of the 'foo' fields for all of the results in the set.
    """
    def __init__(self, result_rows):
        self._rows = result_rows

    def get_single_item(self, item):
        return [r[item] for r in self._rows]

    def __getitem__(self, item):
        # Treat single-value case like multi-value case
        single_value = (type(item) != tuple)
        if single_value:
            item = (item,)
        return [self.get_single_item(i) for i in item]


def find_test_results(name, database):
    """
    Fetches a set of all results for a test with the given name in the
    database.
    :param name: The name of the test to find results for.
    :param database: A path to a pfunk test results database.
    :return: A ResultsDatabaseResultsSet with all of the relevant test results.
    """
    connection = connect_to_database(database)
    results = connection.execute(
        'select identifier from test_results where name like ?'
        'order by pints_committed_date, pfunk_committed_date', [name])
    row_ids = [r[0] for r in results.fetchall()]
    row_readers = [
        ResultsDatabaseReader(connection, row_id) for row_id in row_ids]
    return ResultsDatabaseResultsSet(row_readers)


def connect_to_database(database):
    """
    Establishes a connection to a test results database.
    :param database: A path to a pfunk test results database.
    :return: An open sqlite3 connection to the database.
    """
    connection = sqlite3.connect(database, timeout=30)
    connection.row_factory = sqlite3.Row
    return connection


def find_test_dates(database):
    """
    Returns a dict mapping test names to the time (a ``time.struct_time``) when
    they were last run.
    If a test has not been run, then a default time (Jan 1 1970 00:00:00 UTC)
    is set.
    """
    connection = connect_to_database(database)
    _ensure_database_schema(connection)
    names_and_dates = connection.execute(
        'select name, max(date) as "most_recent" from test_results'
        ' group by name'
    ).fetchall()
    connection.close()
    name_date_map = {
        t[0]: time.strptime(t[1], '%Y-%m-%d-%H:%M:%S') for t in names_and_dates
    }
    for test in pfunk.tests.tests():
        if test not in name_date_map.keys():
            name_date_map[test] = time.struct_time([0] * 9)
    return name_date_map

