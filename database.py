from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
import utils

Base = declarative_base()

class PullRequest(Base):
    __tablename__ = 'pull_requests'

    id = Column(Integer, primary_key = True)
    repo = Column(String)
    number = Column(Integer)
    title = Column(String)
    user_id = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    closed_at = Column(DateTime)
    merged_at = Column(DateTime)

    def __init__(self, owner, repository, pr):
        self.id = pr.id
        self.repo = f"{owner}/{repository}"
        self.number = pr.number
        self.title = pr.title
        self.user_id = pr.user.id
        self.created_at = utils.utc_2_datetime(pr.created_at)
        self.updated_at = utils.utc_2_datetime(pr.updated_at)
        self.closed_at = utils.utc_2_datetime(pr.closed_at) if pr.closed_at is not None else None
        self.merged_at = utils.utc_2_datetime(pr.merged_at) if pr.merged_at is not None else None

class PullRequestFile(Base):
    __tablename__ = 'pull_request_files'

    pr_id = Column(String, ForeignKey('pull_requests.id'), primary_key = True)
    filename = Column(String, primary_key = True)
    status = Column(String)
    additions = Column(Integer)
    deletions = Column(Integer)
    changes = Column(Integer)

    def __init__(self, pr, pr_file):
        self.pr_id = pr.id
        self.filename = pr_file.filename
        self.status = pr_file.status
        self.additions = pr_file.additions
        self.deletions = pr_file.deletions
        self.changes = pr_file.changes

