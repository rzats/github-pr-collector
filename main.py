#!/usr/bin/env python3
"""
A module to analyze insights of PRs in public GitHub repos.
"""

__author__ = "Rostyslav Zatserkovnyi"
__version__ = "1.0.0"

import argparse
import os

from logzero import logger

from github_collector import api, queries, utils

# Possible analytic query options.
MIN_T_MERGE = "min_t_merge"
AVG_T_MERGE = "avg_t_merge"
MAX_T_MERGE = "max_t_merge"
TOP_10_FILES = "top_10_files"


def main(args):
    connection_string = os.getenv("GH_COLLECTOR_CONN_STRING")
    if not connection_string:
        logger.error(
            "could not get PostgreSQL connection string; " +
            "specify it via env variable GH_COLLECTOR_CONN_STRING")
        exit(1)

    if args.which == 'collect':
        try:
            assert len(args.repo.split("/")) == 2
        except AssertionError:
            logger.error(
                "repo must be in the form owner/repository e.g. numpy/numpy")
            exit(1)

        owner = args.repo.split("/")[0]
        repository = args.repo.split("/")[1]

        token = os.getenv("GH_COLLECTOR_API_TOKEN")
        if not token:
            logger.error(
                "could not get API token; " +
                "specify it via env variable GH_COLLECTOR_API_TOKEN")
            exit(1)
        ghapi = api.init_api(token)

        session = queries.init_db_session(connection_string)
        action_collect(session, ghapi, owner, repository, args.resume_page)
    else:
        session = queries.init_db_session(connection_string)
        action_analyze(session)


def action_collect(session, ghapi, owner, repository, resume_page=None):
    """
    Collects pull requests from GitHub repository and adds them to database.

    @param session: SQLAlchemy session.
    @param ghapi: GhApi instance.
    @param owner: The account owning the GitHub repository.
    @param repository: The name of the GitHub repository.
    @param resume_page: The page collection should be resumed from.
    """
    list_pulls = api.list_pulls(ghapi, owner, repository, ascending=True)

    try:
        logger.info(f"Collecting from {owner}/{repository}...")
        for count, page in enumerate(list_pulls):
            # If resume_page is set, skip until that page
            if resume_page is not None and count + 1 < resume_page:
                continue

            # Add all pull requests to database
            logger.debug(f"GET list_pulls {owner}/{repository} | page #{count+1}")
            pulls = [pr for pr in page]

            # If resume_page is set, do not re-insert pulls from that page
            if resume_page is None or count + 1 > resume_page:
                queries.add_pulls(session, pulls, owner, repository)

                # Commit PRs before files, as files rely on pull request IDs
                logger.info(f'Committing PRs for page #{count+1}...')
                session.commit()
                logger.info('...committed successfully!')

            # For each pull request, add files to database
            for pull in pulls:
                logger.debug(
                    f"GET list_files {owner}/{repository}/{pull.number}")
                list_files = api.list_pull_files(ghapi, owner,
                                                 repository,
                                                 pull.number)
                files = []
                for page in list_files:
                    files.extend([file for file in page])
                queries.add_files(session, pull, files)

            # Commit files after all are collected
            logger.info(f'Committing files for PR page #{count+1}...')
            session.commit()
            logger.info('...committed successfully!')
        logger.info(f"Finished successfully!")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        session.rollback()
    finally:
        session.close()

    exit(0)


def action_analyze(session):
    if args.query == TOP_10_FILES:
        query = queries.top_n_files(session, 10)
        result = queries.execute_query(session, query)
        for file in result:
            logger.info(file)
    else:
        if args.query == MIN_T_MERGE:
            query = queries.datediff_min(session)
        elif args.query == AVG_T_MERGE:
            query = queries.datediff_avg(session)
        else: # max_t_merge
            query = queries.datediff_max(session)
        result = queries.execute_query(session, query)[0][0]
        logger.info(f'{utils.seconds_2_human(result)}')
    exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # Add subparser for GitHub API -> Postgres collection
    collect = subparsers.add_parser('collect',
                                    help='Collect PR data from GitHub API.')
    collect.add_argument("repo",
                         help="GitHUb repository to use, e.g. numpy/numpy")
    collect.add_argument("--resume-page", type=int, default=None,
                         help="The page to resume collection from.")
    collect.set_defaults(which='collect')

    # Add subparser for Postgres analytics
    analyze = subparsers.add_parser('analyze',
                                    help='Analyze collected PR data.')
    analyze.add_argument("query",
                         choices=[
                             MIN_T_MERGE,
                             AVG_T_MERGE,
                             MAX_T_MERGE,
                             TOP_10_FILES
                         ],
                         help='The type of query to be run on the database.')
    analyze.set_defaults(which='analyze')

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    main(args)
