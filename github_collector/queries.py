from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func, desc, extract
from github_collector import models

# Common function used in aggregates below.
# Returns the difference between merged/created datetimes for PRs.
DATEDIFF_AGGREGATE = func \
    .trunc(extract('epoch', models.PullRequest.merged_at) -
           extract('epoch', models.PullRequest.created_at)) \
    .label('datediff')


def datediff_min(session):
    """
    @param session: SQLAlchemy session.
    @return: Minimum merged - closed time.
    """
    return session.query(func.min(DATEDIFF_AGGREGATE))\
        .filter(models.PullRequest.merged_at != None)


def datediff_avg(session):
    """
    @param session: SQLAlchemy session.
    @return: Average merged - closed time.
    """
    return session.query(func.avg(DATEDIFF_AGGREGATE))\
        .filter(models.PullRequest.merged_at != None)


def datediff_max(session):
    """
    @param session: SQLAlchemy session.
    @return: Maximum merged - closed time.
    """
    return session.query(func.max(DATEDIFF_AGGREGATE))\
        .filter(models.PullRequest.merged_at != None)


def top_n_files(session, n):
    """
    @param session: SQLAlchemy session.
    @param n: Number of files to display.
    @return: Top N most frequently encountered pull request files.
    """
    return session.query(models.PullRequestFile.filename,
                         func.count(models.PullRequestFile.filename).label(
                             'fc')) \
        .group_by(models.PullRequestFile.filename) \
        .order_by(desc('fc')) \
        .limit(n)


def init_db_session(connection_string):
    """
    Creates a session from a connection string.

    @param connection_string: PostgreSQL connection string.
    @return: SQLAlchemy session.
    """
    db = create_engine(connection_string)
    models.Base.metadata.create_all(db)
    session = sessionmaker(bind=db)()
    return session


def execute_query(session, statement):
    """
    Executes a query based on a lambda function.

    @param session: SQLAlchemy session.
    @param statement: SQLAlchemy query.
    @return: The full result of the query.
    """
    result = session.execute(statement)
    return result.fetchall()


def add_pulls(session, pulls, owner, repository):
    """
    Adds files from a list to database.

    @param session: SQLAlchemy session.
    @param pulls: List of pull requests.
    @param owner: The account owning the GitHub repository.
    @param repository: The name of the GitHub repository.
    """
    db_pulls = [models.PullRequest(pr, owner, repository) for pr in pulls]
    session.add_all(db_pulls)


def add_files(session, pull, files):
    """
    Adds pull requests from a list to database.

    @param session: SQLAlchemy session.
    @param pull: Pull request object.
    @param files: List of pull request files.
    """
    db_files = [models.PullRequestFile(pull, file) for file in files]
    session.add_all(db_files)
