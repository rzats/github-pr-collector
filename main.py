#!/usr/bin/env python3
"""
A module to analyze insights of PRs in public GitHub repos.
"""

__author__ = "Rostyslav Zatserkovnyi"
__version__ = "0.1.0"

import argparse
import os
import api
import database
from logzero import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func, desc, extract, and_

def main(args):
    try:
        assert len(args.repo.split("/")) == 2
    except AssertionError:
        logger.error("repo must be in the form of owner/repository e.g. numpy/numpy")
        exit(1)

    token = os.getenv("GH_COLLECTOR_API_TOKEN")
    if not token:
        logger.error("could not get a token for GitHub API; specify it via env variable GH_COLLECTOR_API_TOKEN")
        exit(1)

    connection_string = os.getenv("GH_COLLECTOR_CONN_STRING")
    if not connection_string:
        logger.error("could not get PostgreSQL connection string; specify it via env variable GH_COLLECTOR_CONN_STRING")
        exit(1)

    owner = args.repo.split("/")[0]
    repository = args.repo.split("/")[1]

    db = create_engine(connection_string)
    database.Base.metadata.create_all(db)
    session = sessionmaker(bind=db)()

    if args.which == 'collect':
        gh_api = api.gh_init_api(token)
        pulls_paginator = api.gh_list_pulls(gh_api, owner, repository)

        try:
            i = 1
            for page in pulls_paginator:
                i += 1

                if i == 3:
                    exit(0)

                print(len(page))
                logger.debug(f"GET list_pulls ${owner}/${repository}")
                pulls = [pr for pr in page]
                db_pulls = [database.PullRequest(owner, repository, pr) for pr in pulls]
                logger.info([pull.id for pull in db_pulls])

                session.add_all(db_pulls)

                for pull in pulls:
                    logger.debug(f"GET list_files {owner}/{repository}/{pull.number}")
                    files_paginator = api.gh_get_files(gh_api, owner, repository, pull.number)
                    files = []
                    for page in files_paginator:
                        files.extend([file for file in page])
                    db_files = [database.PullRequestFile(pull, file) for file in files]
                    logger.info([file.filename for file in db_files])
                    logger.info(len(db_files))
                    session.add_all(db_files)

                session.commit()
        except:
            session.rollback()
        finally:
            session.close()

        exit(0)

    else:
        if args.query == 'min_t_merge':
            statement = session.query(func.min(func.trunc(
                (extract('epoch', database.PullRequest.merged_at) -
                extract('epoch', database.PullRequest.created_at)) / 60).label('datediff')))\
                .filter(database.PullRequest.merged_at != None)
            result = session.execute(statement)
            print(result.fetchall())
        elif args.query == 'avg_t_merge':
            statement = session.query(func.avg(func.trunc(
                (extract('epoch', database.PullRequest.merged_at) -
                extract('epoch', database.PullRequest.created_at)) / 60).label('datediff')))\
                .filter(database.PullRequest.merged_at != None)
            result = session.execute(statement)
            print(result.fetchall())
        elif args.query == 'max_t_merge':
            statement = session.query(func.max(func.trunc(
                (extract('epoch', database.PullRequest.merged_at) -
                extract('epoch', database.PullRequest.created_at)) / 60).label('datediff')))\
                .filter(database.PullRequest.merged_at != None)
            result = session.execute(statement)
            print(result.fetchall())
        else: #top_3_files
            statement = session.query(database.PullRequestFile.filename, func.count(database.PullRequestFile.filename).label('filecount'))\
                .group_by(database.PullRequestFile.filename).order_by(desc('filecount')).limit(3)
            result = session.execute(statement)
            print(result.fetchall())
        exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    collect = subparsers.add_parser('collect', help='Collect pull request data from a given repository.')
    collect.add_argument("repo", help="The repository to use for queries and analytics\ne.g. numpy/numpy")
    collect.set_defaults(which='collect')

    analyze = subparsers.add_parser('analyze', help='Analyze the data collected from a given repository.')
    analyze.add_argument("repo", help="The repository to use for queries and analytics\ne.g. numpy/numpy")
    analyze.add_argument("query", choices=['min_t_merge', 'avg_t_merge', 'max_t_merge', 'top_3_files'],
                         help = 'The type of analytic auery to be run on the database.')
    analyze.set_defaults(which='analyze')

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    main(args)
