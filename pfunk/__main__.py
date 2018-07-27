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
    pfunk.tests.run(name)


def run_next_test():
    """
    Runs the next test.
    """
    import pfunk.tests

    print('NEXT')


def show_test_list():
    """
    Shows the list of tests.
    """
    import pfunk.tests
    for test in pfunk.tests.tests():
        print('  ' + test)


def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description='Run functional tests for Pints.',
    )

    # Run next in line
    parser.add_argument('test_name', nargs='?')
    parser.add_argument(
        '--next',
        action='store_true',
        help='Run the next test in line.',
        )
    parser.add_argument(
        '--list',
        action='store_true',
        help='Show a list of tests that can be run',
        )

    # Parse!
    args = parser.parse_args()
    if args.list:
        show_test_list()
    elif args.next:
        run_next_test()
    elif args.test_name:
        run_named_test(args.test_name)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
