#
# Results DB module.
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2019, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#

from __future__ import print_function
from collections import defaultdict
import sqlite3
import json
import time
import pfunk


class ResultsDatabaseSchemaClient(object):
    """
    Abstract parent for database readers and writers, keeping track of the database columns and how to interpret
    the JSON column.
    """
    primary_columns = ["identifier"]
    mapped_columns = {"commit": "commit_hashes"}
    columns = ["name", "date", "status", "python", "pints", "pints_commit", "pfunk_commit", "commit_hashes", "seed",
               "method"]

    def json_values(self):
        result = self._connection.execute("select json from test_results where identifier = ?",
                                          [self._row])
        json_field = result.fetchone()[0]
        dictionary = {}
        if json_field is not None:
            dictionary = json.loads(json_field)
        return dictionary


class ResultsDatabaseWriter(ResultsDatabaseSchemaClient):
    """
    Provides write access to a SQLite3 database containing test results.
    For compatibility with the interfaces supplied by ResultsWriter/ResultsReader,
    the flat-file equivalents, instances of this class accept a test name and date,
    and provide access to the values in the row matching those properties only.
    """

    def __init__(self, filename, test_name, date):
        self._connection = connect_to_database(filename)
        self.__ensure_schema()
        self._filename = filename
        self._name = test_name
        self._date = date
        self.__ensure_row()

    def __ensure_schema(self):
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
        seed integer,
        method varchar,
        json varchar
        )"""
        self._connection.execute(query)
        self._connection.commit()

    def __ensure_row(self):
        # ensure the row exists
        self._connection.execute("insert into test_results(name,date) values (?,?)", (self._name, self._date))
        self._connection.commit()
        rowID = self._connection.execute("select identifier from test_results where name like ? and date = ?",
                                        (self._name, self._date))
        self._row = rowID.fetchone()[0]

    def __setitem__(self, key, value):
        if key in self.primary_columns:
            # don't update these
            pass
        elif key in self.mapped_columns.keys():
            self[self.mapped_columns[key]] = value
        elif key in self.columns:
            self._connection.execute("update test_results set {} = ? where identifier = ?".format(key),
                                    (value, self._row))
            self._connection.commit()
        else:
            dictionary = self.json_values()
            # workaround: if we're given a numpy array, make a Python list
            if getattr(value, "tolist", None) is not None:
                value = value.tolist()
            dictionary[key] = value
            json_field = json.dumps(dictionary)
            self._connection.execute("update test_results set json = ? where identifier = ?",
                                     (json_field, self._row))
            self._connection.commit()

    def write(self):
        pass

    def filename(self):
        return self._filename


class ResultsDatabaseReader(ResultsDatabaseSchemaClient):
    """
    Provides read access to a row in the test results database.
    """
    def __init__(self, connection, rowID):
        self._connection = connection
        self._row = rowID

    def __getitem__(self, item):
        if item in self.primary_columns or item in self.columns:
            result = self._connection.execute("select {} from test_results where identifier = ?".format(item),
                                              [self._row])
            return result.fetchone()[0]
        if item in self.mapped_columns.keys():
            return self[self.mapped_columns[item]]
        dictionary = defaultdict(lambda: None, self.json_values())
        return dictionary[item]


class ResultsDatabaseResultsSet(object):
    """
    Represents a collection of rows in the test results database. Provides keyed access to the fields in the
    results, so set["foo"] gives you a list of the "foo" fields for all of the results in the set.
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
    Fetches a set of all results for a test with the given name in the database.
    :param name: The name of the test to find results for.
    :param database: A path to a pfunk test results database.
    :return: A ResultsDatabaseResultsSet with all of the relevant test results.
    """
    connection = connect_to_database(database)
    results = connection.execute("select identifier from test_results where name like ?", [name])
    row_ids = [r[0] for r in results.fetchall()]
    row_readers = [ResultsDatabaseReader(connection, row_id) for row_id in row_ids]
    return ResultsDatabaseResultsSet(row_readers)


def connect_to_database(database):
    """
    Establishes a connection to a test results database.
    :param database: A path to a pfunk test results database.
    :return: An open sqlite3 connection to the database.
    """
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    return connection


def find_test_dates(database):
    """
    Returns a dict mapping test names to the time (a ``time.struct_time``) when they were last run.
    If a test has not been run, then a default time (Jan 1 1970 00:00:00 UTC) is set.
    """
    connection = connect_to_database(database)
    names_and_dates = connection.execute('select name, max(date) as "most_recent" from test_results group by name')\
        .fetchall()
    connection.close()
    name_date_map = {t[0]: time.strptime(t[1], "%Y-%m-%d-%H:%M:%S") for t in names_and_dates}
    for test in pfunk.tests.tests():
        if test not in name_date_map.keys():
            name_date_map[test] = time.struct_time([0] * 9)
    return name_date_map
