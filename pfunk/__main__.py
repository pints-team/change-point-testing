#
# Pints functional testing command line utility.
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2018, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
from __future__ import absolute_import, division
from __future__ import print_function, unicode_literals

import os
import argparse
import fnmatch

import pfunk
import pfunk.tests


def list_tests(args):
    """
    Shows all available tests and the date they were last run.
    """
    dates = pfunk.find_test_dates()
    w = max(4, max([len(k) for k in dates.keys()]))
    print('| Name' + ' ' * (w - 4) + ' | Last run            |')
    print('-' * (w + 26))
    for test in sorted(dates.items(), key=lambda x: x[1]):
        name, date = test
        print(
            '| ' + name + ' ' * (w - len(name)) + ' | ' + pfunk.date(date)
            + ' |'
        )


def _parse_pattern(pattern, show_options=True):
    """
    Attempts to match the given pattern to tests, returning a list of matching
    test names.

    If no matches are found an empty list is returned. If ``show_options`` is
    set (default), an error message with a list of options is also displayed.
    """
    # Unix-style pattern matching via fnmatch
    names = []
    for test in pfunk.tests.tests():
        if fnmatch.fnmatch(test, pattern):
            names.append(test)

    # Show options
    if show_options and not names:
        print('No tests found for: "' + pattern + '"')
        print('Options:')
        for test in sorted(pfunk.tests.tests()):
            print('  ' + test)

    return names


def run(args):
    """
    Runs a test.
    """
    # Parse test name, or get next test to run
    if args.name is None:
        names = [pfunk.find_next_test()]
    else:
        names = _parse_pattern(args.name)
    if not names:
        return

    # Run tests
    for name in names:
        for i in range(args.r):
            print('Running test ' + name)
            pfunk.tests.run(name)
        if args.plot or args.show:
            print('Creating plot for ' + name)
            pfunk.tests.plot(name, args.show)

    print('Done')


def plot(args):
    """
    Creates a plot for one or all tests.
    """
    if args.name:
        for name in _parse_pattern(args.name):
            pfunk.tests.plot(name, args.show)
    elif args.all:
        for name in pfunk.tests.tests():
            print('Creating plot for ' + name)
            pfunk.tests.plot(name, args.show)
        print('Done!')


def analyse(args):
    """
    Analyses the result for one or all tests.
    """
    # Parse test name, or get next test to run
    if args.name is None:
        names = [pfunk.find_next_test()]
    else:
        names = _parse_pattern(args.name)
    if not names:
        return

    failed = 0
    for name in names:
        print('Analysing ' + name + ' ... ', end='')
        result = pfunk.tests.analyse(name)
        failed += 0 if result else 1
        print('ok' if result else 'FAIL')

    print()
    print('-'*60)
    print('Ran ' + str(len(names)) + ' tests')

    if failed:
        print('Failed: ' + str(failed))


def generate_report(args):
    """
    Generates a report in Markdown format.
    """
    print('Generating test report')
    pfunk.generate_report()
    print('Done')


def commit_results(args):
    """
    Commits any new results.
    """
    print('Committing new test results')
    pfunk.commit_results()
    print('Done')


def weekend(args):
    """
    Keep running tests, generating reports, and committing results.
    """
    while True:
        pfunk.prepare_pints_repo(force_refresh=True)
        for i in range(10):
            name = pfunk.find_next_test()
            print('Running test ' + name)
            pfunk.tests.run(name)
            pfunk.tests.plot(name)
            print('Done')
            #pfunk.commit_results()
        pfunk.generate_report()
        pfunk.commit_results()


def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description='Run functional tests for Pints.',
    )
    subparsers = parser.add_subparsers(help='commands')

    # Show all debug and info logging messages
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Show debug and info output',
    )

    # Show a list of all available tests
    list_parser = subparsers.add_parser('list', help='List tests')
    list_parser.set_defaults(func=list_tests)

    # Run a test
    run_parser = subparsers.add_parser(
        'run',
        help='Run a test',
    )
    group = run_parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        'name',
        metavar='<name>',
        nargs='?',
        action='store',
        help='The test to run (can be a unix-style pattern)',
    )
    group.add_argument(
        '--next',
        action='store_true',
        help='Run the next test',
    )
    run_parser.add_argument(
        '--plot',
        action='store_true',
        help='Create a plot after testing',
    )
    run_parser.add_argument(
        '--show',
        action='store_true',
        help='Create and show a plot after testing.',
    )
    run_parser.add_argument(
        '-r', default=1, type=int,
        help='Number of test repeats to run.',
    )
    run_parser.set_defaults(func=run)

    # Plot one or all test results
    plot_parser = subparsers.add_parser(
        'plot',
        help='Plot one or all test results'
    )
    group = plot_parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        'name',
        metavar='<name>',
        nargs='?',
        action='store',
        help='The plot to create (can be a unix-style pattern)',
    )
    group.add_argument(
        '--all',
        action='store_true',
        help='Create plots for all tests',
    )
    plot_parser.add_argument(
        '--show',
        action='store_true',
        help='Show plots on screen',
    )
    plot_parser.set_defaults(func=plot)

    # Analyse one or all test results
    analyse_parser = subparsers.add_parser(
        'analyse',
        help='Analyse one or all test results'
    )
    group = analyse_parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        'name',
        metavar='<name>',
        nargs='?',
        action='store',
        help='The test to analyse',
    )
    group.add_argument(
        '--all',
        action='store_true',
        help='Analyse all tests',
    )
    analyse_parser.set_defaults(func=analyse)

    # Compile a report of test results
    report_parser = subparsers.add_parser(
        'report',
        help='Generate a test report',
    )
    report_parser.set_defaults(func=generate_report)

    # Commit any new test results
    commit_parser = subparsers.add_parser(
        'commit',
        help='Commit any new test results',
    )
    commit_parser.set_defaults(func=commit_results)

    # Keep running tests, generating reports, and committing results
    weekend_parser = subparsers.add_parser(
        'weekend',
        help='Keep running tests, generating reports, and committing results',
    )
    weekend_parser.set_defaults(func=weekend)

    # Parse!
    args = parser.parse_args()
    if 'func' in args:
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
