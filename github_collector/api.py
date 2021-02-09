import time

from ghapi.core import GhApi
from ghapi.page import paged
from logzero import logger

from github_collector import utils

# The number of requests inbetween logging API quota
API_LOGGING_FREQUENCY = 100

# Size of a page to be used in paginated requests (maximum of 100 is used)
API_PAGE_SIZE = 100

# The number of remaining requests at which the script will temporarily halt
API_QUOTA_THRESHOLD = 10

# Timeout for API requests, used to prevent a hanging issue in ghapi
API_REQUEST_TIMEOUT = 100


def init_api(token):
    """
    Creates a GitHub API instance with set token and rate limit callbacks.

    @param token: GitHub API token (see https://github.com/settings/tokens).
    @return: a GhApi instance.
    """
    # Hotfix for https://github.com/fastai/ghapi/issues/28
    #fastcore.net._opener.open = functools.partial(fastcore.net._opener.open,
    #                                              timeout=API_REQUEST_TIMEOUT)

    # Initialize API with GitHub token
    api = GhApi(
        token=token
    )

    # Define limit_cb (called after each API request with rate limit info)
    def limit_callback(rem, quota):
        # Periodically print remaining quota
        if rem % API_LOGGING_FREQUENCY == 0:
            logger.info(f"Remaining API requests per hour: {rem} of {quota}")

        # Once the quota is close enough to ending, wait until it cools down
        if rem == API_QUOTA_THRESHOLD:
            # Reset the callback for the next rate_limit.get() call
            api.limit_cb = None

            # Get the timestamp at which the quota will be reset
            limits = api.rate_limit.get()
            reset = limits.resources.core.reset

            # Sleep until that timestamp
            logger.warn("Close to reaching API rate limit. " +
                        f"Halting until {utils.unix_2_utc(reset)}...")
            while int(time.time()) <= reset:
                time.sleep(1)
            logger.warn("Rate limit is reset, resuming...")

            # Restore the callback to this function again
            api.limit_cb = limit_callback

    api.limit_cb = limit_callback
    return api


def list_pulls(api, owner, repository, ascending=False):
    """
    Creates a GitHub API iterator that returns all pull requests
    in a given repository, sorted by last updated time.

    @param api: GhApi instance.
    @param owner: The account owning the GitHub repository.
    @param repository: The name of the GitHub repository.
    @param ascending: Whether the results should be sorted in ascending order.
    @return: GhApi paging iterator object.
    """
    direction = 'asc' if ascending else 'desc'
    return paged(api.pulls.list, owner=owner, repo=repository, state='all',
                 sort='updated', direction=direction,
                 per_page=API_PAGE_SIZE)


def list_pull_files(api, owner, repository, pull_num):
    """
    Creates a GitHub API iterator that returns all files
    in a given pull request.

    @param api: GhApi instance.
    @param owner: The account owning the GitHub repository.
    @param repository: The name of the GitHub repository.
    @param pull_num: The number of the given pull request.
    @return: GhApi paging iterator object.
    """
    return paged(api.pulls.list_files, owner=owner, repo=repository,
                 pull_number=pull_num,
                 per_page=API_PAGE_SIZE)
