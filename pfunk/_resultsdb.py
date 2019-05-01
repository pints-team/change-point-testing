#
# Results DB module.
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2019, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#

from __future__ import print_function
import sqlite3

# String types in Python 2 and 3
try:
    basestring
except NameError:
    basestring = str


class ResultsDatabase(object):
    """
    Provides read-write access to a SQLite3 database containing test results.
    For compatibility with the interfaces supplied by ResultsWriter/ResultsReader,
    the flat-file equivalents, instances of this class accept a test name and date,
    and provide access to the values in the row matching those properties only.
    """

    primary_columns = ["name", "date"]
    mapped_columns = {"commit":"commit_hashes"}
    columns = ["status", "python", "pints", "pints_commit", "pfunk_commit", "commit_hashes", "seed", "method"]

    def __init__(self, filename, test_name, date):
        self._connection = sqlite3.connect(filename)
        self._connection.row_factory = sqlite3.Row
        self.__ensure_schema()
        self._filename = filename
        self._name = test_name
        self._date = date
        self.__ensure_row()

    def __ensure_schema(self):
        cursor = self._connection.cursor()
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
        cursor.execute(query)
        cursor.close()

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
            print("Silently ignoring {}:{}".format(key, value))

    def write(self):
        pass

    def filename(self):
        return self._filename

    def __getitem__(self, item):
        print("Unknown item {}".format(item))
        return None
