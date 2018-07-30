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


def run_named_test(name):
    """
    Runs the test ``name``.
    """
    import pfunk.tests
    try:
        pfunk.tests.run(name)
    except KeyError:
        print('Test not found: ' + name)
        print('Available tests:')
        for test in pfunk.tests.tests():
            print('  ' + test)


def run_next_test():
    """
    Runs the next test.
    """
    import pfunk
    import pfunk.tests
    next = pfunk.find_next_test()
    pfunk.tests.run(next)


def show_test_list():
    """
    Shows the list of tests.
    """
    import pfunk
    dates = pfunk.find_test_dates()
    w = 1 + max([len(k) for k in dates.keys()])
    for test in sorted(dates.items(), key=lambda x: x[1]):
        name, date = test
        print(name + ' ' * (w - len(name)) + pfunk.date(date))


def run_named_plot(name):
    """
    Runs the plot ``name``.
    """
    import pfunk.plots
    try:
        pfunk.plots.run(name)
    except KeyError:
        print('Plot not found: ' + name)
        print('Available plots:')
        for plot in pfunk.plots.plots():
            print('  ' + plot)


def run_all_plots():
    """
    Runs all plots.
    """
    import pfunk.plots
    for name in pfunk.plots.plots():
        pfunk.plots.run(name)


def show_plot_list():
    """
    Shows the list of plots.
    """
    import pfunk.plots
    for k in pfunk.plots.plots():
        print('  ' + k)


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
        '--plots',
        action='store_true',
        help='Show a list of plots that can be run',
    )
    parser.add_argument(
        '--allplots',
        action='store_true',
        help='Run all plots',
    )

    # Parse!
    args = parser.parse_args()
    if args.tests:
        show_test_list()
    elif args.plots:
        show_plot_list()
    elif args.next:
        run_next_test()
    elif args.t:
        run_named_test(args.t[0])
    elif args.p:
        run_named_plot(args.p[0])
    elif args.allplots:
        run_all_plots()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
