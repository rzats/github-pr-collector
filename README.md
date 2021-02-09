# github-pr-collector
A CLI tool to collect insights from public repositories, store them in a relational DB and analyze them.

### Requirements (tested on macOS Mojave)

- Python 3 & pip
- pipenv (e.g. `brew install pipenv`)
- PostgreSQL (e.g. `brew install postgresql`)

### Usage

Set up a pipenv and install the necessary dependencies:
- `pipenv --three`
- `pipenv --install`

Set up a PostgreSQL database; either a local instance or e.g. RDS:
- `brew services start postgresql`
- `createdb`

Obtain an API token from https://github.com/settings/tokens, then temporarily export it as an environment variable. Do the same with a PostgreSQL connection string (a local default is shown here):

- `export GH_COLLECTOR_API_TOKEN = c9a43a55b23972585e45507f2993f1133a758cbc`
- `export GH_COLLECTOR_CONN_STRING = postgresql://localhost:5432`

Finally, run the Python script as follows:

- `pipenv run python main.py --help`

### Example

The utility has been tested on the [numpy/numpy](https://github.com/numpy/numpy) repository containing 9057 pull requests as follows:
```
$ pipenv run python main.py collect numpy/numpy
```

_(note that the script above is very long-running - for numpy it takes around 3.5 hours due to API rate limiting cool-offs)_

This has resulted in the following number of entities:
```
# select count(*) from pull_requests;
 count
-------
  9057
```

```
# select count(*) from pull_request_files;
 count
-------
 42970
```

The results of all analytics queries are as follows:

1\. Minimum time to merge a PR.

```
$ pipenv run python main.py analyze min_t_merge
[I 210209 21:32:06 main:130] 0 day(s), 0 hour(s), 0 minute(s), 8 second(s)
```

2\. Maximum time to merge a PR.

```
$ pipenv run python main.py analyze max_t_merge
[I 210209 21:32:27 main:130] 1735 day(s), 8 hour(s), 15 minute(s), 17 second(s)
```

3\. Average time to merge a PR.
```
$ pipenv run python main.py analyze avg_t_merge
[I 210209 21:32:43 main:130] 13 day(s), 3 hour(s), 2 minute(s), 6 second(s)
```

4\. Top 10 most frequently modified files, with number of PR references.

```
$ pipenv run python main.py analyze top_10_files
[I 210209 21:34:24 main:120] ('numpy/core/tests/test_multiarray.py', 690)
[I 210209 21:34:24 main:120] ('numpy/lib/function_base.py', 466)
[I 210209 21:34:24 main:120] ('numpy/ma/core.py', 374)
[I 210209 21:34:24 main:120] ('numpy/core/src/multiarray/multiarraymodule.c', 352)
[I 210209 21:34:24 main:120] ('numpy/lib/tests/test_function_base.py', 331)
[I 210209 21:34:24 main:120] ('numpy/core/src/multiarray/ctors.c', 324)
[I 210209 21:34:24 main:120] ('numpy/core/numeric.py', 293)
[I 210209 21:34:24 main:120] ('numpy/core/tests/test_regression.py', 283)
[I 210209 21:34:24 main:120] ('numpy/ma/tests/test_core.py', 283)
[I 210209 21:34:24 main:120] ('numpy/lib/npyio.py', 277)
```