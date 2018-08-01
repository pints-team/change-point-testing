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

import argparse
import pfunk
import pfunk.tests


def print_avail_tests(name):
    print('Plot not found: ' + name)
    print('Available tests:')
    for test in pfunk.tests.tests():
        print('  ' + test)


def run_named_test(name):
    """
    Runs the test ``name``.
    """
    try:
        pfunk.tests.run(name)
    except KeyError:
        print_avail_tests(name)


def run_next_test():
    """
    Runs the next test.
    """
    next = pfunk.find_next_test()
    pfunk.tests.run(next)


def show_test_list():
    """
    Shows the list of tests.
    """
    dates = pfunk.find_test_dates()
    w = 1 + max([len(k) for k in dates.keys()])
    for test in sorted(dates.items(), key=lambda x: x[1]):
        name, date = test
        print(name + ' ' * (w - len(name)) + pfunk.date(date))


def run_named_plot(name, show=False):
    """
    Runs the plot ``name``.
    """
    try:
        pfunk.tests.plot(name, show)
    except KeyError:
        print_avail_tests(name)


def run_all_plots(show=False):
    """
    Runs all plots.
    """
    for name in pfunk.tests.tests():
        pfunk.tests.plot(name, show)


def run_named_analyse(name, show=False):
    """
    Runs the analyse ``name``.
    """
    try:
        pfunk.tests.analyse(name)
    except KeyError:
        print_avail_tests(name)


def run_all_analyse(show=False):
    """
    Runs all analyse.
    """
    for name in pfunk.tests.tests():
        pfunk.tests.analyse(name)


def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description='Run functional tests for Pints.',
    )

    # Run next in line
    parser.add_argument(
        '-t',
        metavar='test_name',
        nargs=1,
        help='Run a specific test',
    )
    parser.add_argument(
        '-p',
        metavar='plot_name',
        nargs=1,
        help='Run a specific plot',
    )
    parser.add_argument(
        '--next',
        action='store_true',
        help='Run the next test in line.',
    )
    parser.add_argument(
        '--tests',
        action='store_true',
        help='Show a list of tests that can be run',
    )
    parser.add_argument(
        '--allplots',
        action='store_true',
        help='Run all plots',
    )
    parser.add_argument(
        '--show',
        action='store_true',
        help='Show plots as well as saving them.',
    )

    # Parse!
    args = parser.parse_args()
    if args.tests:
        show_test_list()
    elif args.next:
        run_next_test()
    elif args.t:
        run_named_test(args.t[0])
    elif args.p:
        run_named_plot(args.p[0], args.show)
    elif args.allplots:
        run_all_plots(args.show)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
