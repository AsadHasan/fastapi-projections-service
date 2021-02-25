![example workflow name](https://github.com/AsadHasan/fastapi-projections-service/workflows/Deploy/badge.svg)
[![codecov](https://codecov.io/gh/AsadHasan/fastapi-projections-service/branch/main/graph/badge.svg?token=7YSS3MAKQD)](https://codecov.io/gh/AsadHasan/fastapi-projections-service)
# FastAPI projections service

Playing with FastAPI, by creating a _very over-simplified_ investment projections service (with projections calculated by [Nutmeg's calculator](https://try.nutmeg.com/)), deployed on Heroku, as part of GitHub Actions CD pipeline; and Docker image also pushed to GitHub packages.

## Projections service usage documentation

1. [Swagger UI](https://fastapi-projections-service.herokuapp.com/docs)
2. [Redoc](https://fastapi-projections-service.herokuapp.com/redoc)

## Dev tooling and QA measures used

### Tests 
1. Unit and integration tests: Executed on Push and PRs, before Docker image is built. Code coverage measured by Codecov.
2. End to end test: Executed on Push and PRs, _after_ Docker image is built, and _before_ it is pushed to GitHub packages; and then once again _after_ Docker image is tagged and pushed to Heroku and service deployed.
3. OWASP API security scan: Executed on Push and PRs, after end-to-end test has run.

### Dependency updates
PRs opened for dependency updates by Dependabot Bot and those PRs auto-merged after successful CI checks by Mergify.

### Static code analysis
Codeql and OSSAR scans, via GitHub Actions, on Push and PRs.

### Pre commit checks
Following checks/scans made by Pre-commit: Pylint, Flake8, Black, Mypy and isort.

### CI and CD
GitHub Actions and Heroku
