#!/usr/bin/env python3
"""
A module to collect request data from a public GitHub repository to a database.
"""

__author__ = "Rostyslav Zatserkovnyi"
__version__ = "0.1.0"

import argparse
from logzero import logger


def main(args):
    logger.info("Hello, world!")
    logger.info(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    collect = subparsers.add_parser('collect', help='Collect pull request data from a given repository.')
    collect.add_argument("repo", help="The repository to use for queries and analytics\ne.g. numpy/numpy")
    collect.add_argument('-r', '--refresh', action='store_true', default=False,
                         help = 'Update pull requests based on timestamp rather than restarting from scratch.')

    analyze = subparsers.add_parser('analyze', help='Analyze the data collected from a given repository.')
    analyze.add_argument("repo", help="The repository to use for queries and analytics\ne.g. numpy/numpy")
    analyze.add_argument('--query', choices=['min_t_merge', 'avg_t_merge', 'max_t_merge', 'top_3_files', 'contrib_merge_ratio'],
                         help = 'The type of analytic auery to be run on the database.')

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    main(args)
