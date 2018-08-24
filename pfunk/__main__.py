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


def run(args):
    """
    Runs a test.
    """
    name = args.name if args.name else pfunk.find_next_test()
    print('Running test ' + name)
    pfunk.tests.run(name)
    print('Done')


def plot(args):
    """
    Creates a plot for one or all tests.
    """
    if args.name:
        pfunk.tests.plot(args.name, args.show)
    elif args.all:
        for name in pfunk.tests.tests():
            print('Creating plot for ' + name)
            pfunk.tests.plot(name, args.show)
        print('Done!')


def analyse(args):
    """
    Analyses the result for one or all tests.
    """
    tests = [args.name] if args.name else pfunk.tests.tests()
    failed = 0
    for name in tests:
        print('Analysing ' + name + ' ... ', end='')
        result = pfunk.tests.analyse(name)
        failed += 0 if result else 1
        print('ok' if result else 'FAIL')

    print()
    print('-'*60)
    print('Ran ' + str(len(tests)) + ' tests')

    if failed:
        print('Failed: ' + str(failed))


def generate_report(args):
    """
    Generates a report in Markdown format.
    """
    print('Generating test report')
    filename = os.path.join(pfunk.DIR_PFUNK, 'report.md')
    print('Storing in ' + filename)
    pfunk.generate_report(filename)
    print('Done')


def commit_results(args):
    """
    Commits any new results.
    """
    print('Committing new test results')
    pfunk.commit_results()
    print('Done')


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
        choices=pfunk.tests.tests(),
        action='store',
        help='The test to run',
    )
    group.add_argument(
        '--next',
        action='store_true',
        help='Run the next test',
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
        choices=pfunk.tests.tests(),
        action='store',
        help='The plot to create',
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
        choices=pfunk.tests.tests(),
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

    # Parse!
    args = parser.parse_args()
    if 'func' in args:
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
