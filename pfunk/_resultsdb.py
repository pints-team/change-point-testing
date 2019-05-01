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


class ResultsDatabaseSchemaClient(object):
    primary_columns = ["name", "date"]
    mapped_columns = {"commit": "commit_hashes"}
    columns = ["status", "python", "pints", "pints_commit", "pfunk_commit", "commit_hashes", "seed", "method"]

    def json_values(self):
        result = self._connection.execute("select json from test_results where name like ? and date = ?",
                                          (self._name, self._date))
        json_field = result.fetchone()[0]
        dictionary = {}
        if json_field is not None:
            dictionary = json.loads(json_field)
        return dictionary


class ResultsDatabaseWriter(ResultsDatabaseSchemaClient):
    """
    Provides read-write access to a SQLite3 database containing test results.
    For compatibility with the interfaces supplied by ResultsWriter/ResultsReader,
    the flat-file equivalents, instances of this class accept a test name and date,
    and provide access to the values in the row matching those properties only.
    """

    def __init__(self, filename, test_name, date):
        self._connection = sqlite3.connect(filename)
        self._connection.row_factory = sqlite3.Row
        self.__ensure_schema()
        self._filename = filename
        self._name = test_name
        self._date = date
        self.__ensure_row()

    def __ensure_schema(self):
        query = """ create table if not exists test_results(
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
        json varchar,
        primary key (name, date)
        )"""
        self._connection.execute(query)
        self._connection.commit()

    def __ensure_row(self):
        # ensure the row exists
        self._connection.execute("insert into test_results(name,date) values (?,?)", (self._name, self._date))
        self._connection.commit()

    def __setitem__(self, key, value):
        if key in self.primary_columns:
            # don't update these
            pass
        elif key in self.mapped_columns.keys():
            self[self.mapped_columns[key]] = value
        elif key in self.columns:
            self._connection.execute("update test_results set {} = ? where name like ? and date = ?".format(key),
                                    (value, self._name, self._date))
            self._connection.commit()
        else:
            dictionary = self.json_values()
            # workaround: if we're given a numpy array, make a Python list
            if getattr(value, "tolist", None) is not None:
                value = value.tolist()
            dictionary[key] = value
            json_field = json.dumps(dictionary)
            self._connection.execute("update test_results set json = ? where name like ? and date = ?",
                                     (json_field, self._name, self._date))
            self._connection.commit()

    def write(self):
        pass

    def filename(self):
        return self._filename


class ResultsDatabaseReader(ResultsDatabaseSchemaClient):
    def __init__(self, connection, testname, date):
        self._connection = connection
        self._name = testname
        self._date = date

    def __getitem__(self, item):
        if item in self.primary_columns or item in self.columns:
            result = self._connection.execute("select {} from test_results where name like ? and date = ?".format(item),
                                              (self._name, self._date))
            return result.fetchone()[0]
        if item in self.mapped_columns.keys():
            return self[self.mapped_columns[item]]
        dictionary = defaultdict(lambda: None, self.json_values())
        return dictionary[item]


class ResultsDatabaseResultsSet(object):
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
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    results = connection.execute("select date from test_results where name like ?", [name])
    dates = [r[0] for r in results.fetchall()]
    row_readers = [ResultsDatabaseReader(connection, name, date) for date in dates]
    return ResultsDatabaseResultsSet(row_readers)
