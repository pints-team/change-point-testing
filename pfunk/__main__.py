#
# Pints functional testing command line utility.
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2019, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
import argparse
import fnmatch
import multiprocessing
import os
import subprocess
import sys

from itertools import product

import pfunk
import pfunk.tests


# Debug warnings
#import warnings
#warnings.filterwarnings('error', category=FutureWarning)


def list_tests(args):
    """
    Shows all available tests and the date they were last run.
    """
    if args.next:
        # Show next test only
        print(pfunk.find_next_test(args.database))
        return

    # Show table of tests
    dates = pfunk.find_test_dates(args.database)
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
        names = [pfunk.find_next_test(args.database)]
    else:
        names = _parse_pattern(args.name)
    if not names:
        return

    # Update pints repository
    if not args.no_refresh:
        print('Refreshing Pints repository')
        pfunk.pintsrepo.pull()

    # Allow testing of older pints versions
    if args.commit:

        # Check analysing and plotting is disabled
        if args.analyse or args.plot or args.show:
            print('When testing specific commits, plots and/or'
                  ' analysis cannot be run.')
            sys.exit(1)

        # Check out alternative pints version
        print(f'Checking out {args.commit}')
        pfunk.pintsrepo.checkout(args.commit)
        print(pfunk.pintsrepo.info())

    # Prepare module
    pfunk.pintsrepo.prepare_module()
    pfunk.pfunkrepo.prepare_module()

    # Multi-processing
    nproc = min(args.r, multiprocessing.cpu_count() - 2)

    # Run tests
    for name in names:
        # Run the test args.r times
        if nproc > 1:
            # Run in parallel
            with multiprocessing.Pool(processes=nproc) as pool:
                print(f'Running {name} {args.r} times with {nproc} processes:',
                      flush=True)

                # Starmap with product of name and
                # range: -> [(name, 0), (name, 1), ...]
                pool.starmap(
                    pfunk.tests.run,
                    product([name], [args.database], range(args.r))
                )
        else:
            # Run without multiprocessing
            print(f'Running {name} {args.r} times without multiprocessing')
            for i in range(args.r):
                pfunk.tests.run(name, args.database, i)

        if args.analyse:
            print('Analysing ' + name + ' ... ', end='')
            result = pfunk.tests.analyse(name, args.database)
            print('ok' if result else 'FAIL')

        if args.plot or args.show:
            print('Creating plot for ' + name)
            pfunk.tests.plot(name, args.database, args.show)

    print('Done')


def plot(args):
    """
    Creates a plot for one or all tests.
    """
    # Make plots
    if args.name:
        for name in _parse_pattern(args.name):
            pfunk.tests.plot(name, args.database, args.show)
    elif args.all:
        for name in pfunk.tests.tests():
            print('Creating plot for ' + name)
            pfunk.tests.plot(name, args.database, args.show)
        print('Done!')


def analyse(args):
    """
    Analyses the result for one, the most recent, or all tests
    """

    # Parse test name, or get next test to run
    if args.all:
        names = sorted(pfunk.tests.tests())
    elif args.last:
        names = [pfunk.find_previous_test(args.database)]
    elif args.name is None:
        names = [pfunk.find_next_test(args.database)]
    else:
        names = _parse_pattern(args.name)

    if not names:
        return

    failed = 0
    for name in names:
        print('Analysing ' + name + ' ... ', end='')
        result = pfunk.tests.analyse(name, args.database)
        failed += 0 if result else 1
        print('ok' if result else 'FAIL')
        if not result:
            print('{} failed'.format(name), file=sys.stderr)

    print()
    print('-' * 60)
    print('Ran ' + str(len(names)) + ' tests')

    if failed:
        print('Failed: ' + str(failed))


def generate_report(args):
    """
    Generates a report in Markdown format.
    """
    print('Generating test report')
    pfunk.generate_report(args.database)
    print('Done')


def upload_results(args):
    """
    Commits any new results.
    """
    print('Committing new test results')
    pfunk.website.upload_results()
    print('Done')


def investigate(args):
    """
    Systematically check out all commits, starting from a given minimum commit,
    perform N runs of a given test, and plot the results.
    """
    # TODO Unfortunately can't use bisection or something clever at the moment
    # because the results are ordered by the date the test was run.

    # Get test names
    names = _parse_pattern(args.name[0])

    # Update pints repo
    pfunk.pintsrepo.pull()

    # Get commits to look at
    if args.n:
        if args.n < 1:
            print('Number of commits must be 1 or more.')
            sys.exit(1)
        commits = pfunk.pintsrepo.latest_commits(args.n)
    else:
        commits = pfunk.pintsrepo.commits_since(args.c)

    # Get number of repeats
    repeats = args.r
    if repeats < 1:
        print('Number of repeats must be 1 or more.')
        sys.exit(1)

    # Run tests in subprocesses
    base = [
        sys.executable,
        sys.argv[0],
        'run', args.name[0],
        '-r', str(repeats),
        '--database', args.database,
        '--no-refresh',
    ]

    for commit in commits:
        cmd = base + ['-commit', commit]
        try:
            p = subprocess.Popen(cmd)
            p.wait()
        except KeyboardInterrupt:
            p.terminate()
            print('ABORTED')
            return

        if p.returncode != 0:
            print(f'RUN FAILED FOR COMMIT {commit}')

    # Analyse results
    for name in names:
        pfunk.tests.plot(name, args.database, args.show)


class CleanFileAction(argparse.Action):
    """
    Turn a path in a command-line argument into a "clean" (absolute, with ~
    expanded) path.

    Examples::

        ./foo -> /wherever/pwd/is/foo
        ~/foo -> /home/pints-user/foo

    """
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, pfunk.clean_filename(values))


def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description='Run functional tests for Pints.',
    )
    subparsers = parser.add_subparsers(help='commands')

    # Show a list of all available tests
    list_parser = subparsers.add_parser('list', help='List tests')
    list_parser.add_argument(
        '--next',
        action='store_true',
        help='Show only the next scheduled test',
    )
    list_parser.add_argument(
        '--database',
        action=CleanFileAction,
        default=pfunk.DEFAULT_RESULTS_DB,
        help="A SQLite database in which to find previous test results.",
    )
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
        '--analyse',
        action='store_true',
        help='Analyse the test result after running.',
    )
    run_parser.add_argument(
        '--database',
        action=CleanFileAction,
        default=pfunk.DEFAULT_RESULTS_DB,
        help='A SQLite database in which to store run results. Will be created'
             ' if it doesn\'t exist.',
    )
    run_parser.add_argument(
        '-r', default=1, type=int,
        help='Number of test repeats to run.',
    )
    run_parser.add_argument(
        '-commit', nargs=1, type=str,
        help='Test a specific Pints commit',
    )
    run_parser.add_argument(
        '--no-refresh',
        action='store_true',
        help='Don\'t attempt to refresh (pull) the pints repository',
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
    plot_parser.add_argument(
        '--database',
        action=CleanFileAction,
        default=pfunk.DEFAULT_RESULTS_DB,
        help="A SQLite database in which to find previous test results.",
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
    group.add_argument(
        '--last',
        action='store_true',
        help='Analyse most recently run test. Used for Azure CI.',
    )
    analyse_parser.add_argument(
        '--database',
        action=CleanFileAction,
        default=pfunk.DEFAULT_RESULTS_DB,
        help='Test results database',
    )
    analyse_parser.set_defaults(func=analyse)

    # Compile a report of test results
    report_parser = subparsers.add_parser(
        'report',
        help='Generate a test report',
    )
    report_parser.add_argument(
        '--database',
        action=CleanFileAction,
        default=pfunk.DEFAULT_RESULTS_DB,
        help='Test results database',
    )
    report_parser.set_defaults(func=generate_report)

    # Commit any new test results
    commit_parser = subparsers.add_parser(
        'commit',
        help='Commit any new test results',
    )
    commit_parser.set_defaults(func=upload_results)

    # Keep running tests, generating reports, and committing results
    #weekend_parser = subparsers.add_parser(
    #    'weekend',
    #    help='Keep running tests, generating reports, and committing results',
    #)
    #weekend_parser.set_defaults(func=weekend)

    # Investigate when a specific change happened
    investigate_parser = subparsers.add_parser(
        'investigate',
        help='Find out when a specific change happened, by running tests on'
             ' the last N commits, and storing the results in a custom'
             ' directory.'
    )
    investigate_parser.add_argument(
        'name',
        metavar='<name>',
        nargs=1,
        action='store',
        help='The test to investigate',
    )
    group = investigate_parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-c',
        metavar='<commit>',
        type=str,
        action='store',
        help='The first commit to test',
    )
    group.add_argument(
        '-n',
        metavar='<n>',
        type=int,
        action='store',
        help='The number of commits to look back',
    )
    investigate_parser.add_argument(
        '-r', default=3, type=int,
        help='Number of test repeats to run (default 3).',
    )
    investigate_parser.add_argument(
        '--show',
        action='store_true',
        help='Show plots on screen',
    )
    investigate_parser.add_argument(
        '--database',
        action=CleanFileAction,
        default=pfunk.DEFAULT_RESULTS_DB,
        help='Test results database',
    )
    investigate_parser.set_defaults(func=investigate)

    # Parse!
    args = parser.parse_args()

    if 'func' in args:
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)

    main()
