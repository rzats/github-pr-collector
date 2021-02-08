from ghapi.core import GhApi
from ghapi.page import paged
import fastcore.net
import functools
import utils
import time
from logzero import logger

def gh_init_api(token):
    # Hotfix for https://github.com/fastai/ghapi/issues/28
    fastcore.net._opener.open = functools.partial(fastcore.net._opener.open, timeout=10)

    # Initialize API with GitHub token
    api = GhApi(
        token=token
    )

    def limit_callback(rem, quota):
        # Periodically print remaining quota
        if rem % 100 == 0:
            logger.info(f"Remaining API requests per hour: {rem} of {quota}")

        # Once the quota is close enough to ending, wait until it cools down
        if rem <= 10:
            # Reset the callback for the rate_limit.get() call, preventing an endless loop
            api.limit_cb = None

            limits = api.rate_limit.get()
            reset = limits.resources.core.reset

            logger.warn(f"Close to reaching a rate limit. Halting until {utils.unix_2_utc(reset)}...")
            while int(time.time()) <= reset:
                time.sleep(1)
            logger.warn(f"Rate limit reset, resuming")

            # Restore the callback to its regular state
            api.limit_cb = limit_callback

    api.limit_cb = limit_callback
    return api

def gh_list_pulls(api, owner, repository, ascending=False):
    direction = 'asc' if ascending else 'desc'
    return paged(api.pulls.list, owner=owner, repo=repository, state='all', sort='updated', direction=direction, per_page=50)

def gh_get_files(api, owner, repository, pull_num):
    return paged(api.pulls.list_files, owner=owner, repo=repository, pull_number=pull_num, per_page=50)


