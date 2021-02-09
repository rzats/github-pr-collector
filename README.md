# github-pr-collector
Analysing insights of PRs in public GitHub repos.

### Requirements (tested on macOS Mojave)

- Python 3 & pip
- pipenv (e.g. `brew install pipenv`)
- PostgreSQL (e.g. `brew install postgresql`)

### Usage

- `pipenv --three`
- `pipenv --install`
- `brew services start postgresql`
- `createdb`

https://github.com/settings/tokens

- `export GH_COLLECTOR_API_TOKEN = c9a43a55b23972585e45507f2993f1133a758cbc`
- `export GH_COLLECTOR_CONN_STRING = postgresql://localhost:5432`
- `pipenv run python main.py --help`

### Example

```
$ pipenv run python main.py collect numpy/numpy
```

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

```
$ pipenv run python main.py analyze min_t_merge
[I 210209 21:32:06 main:130] 0 day(s), 0 hour(s), 0 minute(s), 8 second(s)
```

```
$ pipenv run python main.py analyze max_t_merge
[I 210209 21:32:27 main:130] 1735 day(s), 8 hour(s), 15 minute(s), 17 second(s)
```

```
$ pipenv run python main.py analyze avg_t_merge
[I 210209 21:32:43 main:130] 13 day(s), 3 hour(s), 2 minute(s), 6 second(s)
```

```
$ pipenv run python main.py analyze top_10_files
pipenv run python main.py analyze top_10_files
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