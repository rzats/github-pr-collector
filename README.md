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