# Server with CI/CD

___
The simple multi-threads server.
With CI/CD and Docker

![example workflow](https://github.com/MaksKos/server_ci_cd/actions/workflows/integration.yaml/badge.svg)
![example workflow](https://github.com/MaksKos/server_ci_cd/actions/workflows/deploy.yaml/badge.svg)

## How it's work
There is two branches:

 * `main`
 * `dev`

__Push__ in `dev` branch call `integration.yaml` in GitHub Actions. Check the lint by __flake8__ and generate the artefacts by __coverage__.

After __Pull requests__ in `main` branch `deploy.yaml` build docker image and push it to __DockerHub__ then deploy this image on server.
