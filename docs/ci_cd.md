# CI/CD Pipeline Documentation

## Overview

The Heart of News backend uses a continuous integration and continuous deployment (CI/CD) pipeline implemented with GitHub Actions. This pipeline automates testing, linting, building, and deployment processes.

## Pipeline Structure

The CI/CD pipeline consists of the following stages:

1. **Testing**: Run unit, integration, and end-to-end tests
2. **Linting**: Check code style and quality
3. **Building**: Build Docker images
4. **Deployment**: Deploy to staging or production environments

## Workflows

### Main Workflow (`.github/workflows/main.yml`)

This workflow runs on pushes to `main` and `develop` branches, as well as pull requests to these branches.

#### Jobs:

1. **Test**
   - Sets up Python environment
   - Installs dependencies
   - Runs pytest with coverage
   - Uploads coverage report to Codecov

2. **Lint**
   - Runs Black for code formatting
   - Runs isort for import sorting
   - Runs flake8 for code quality checks

3. **Build and Push**
   - Runs after successful test and lint jobs
   - Only runs on pushes to `main` or `develop`
   - Builds Docker image
   - Pushes image to Docker Hub

4. **Deploy Staging**
   - Runs after successful build job
   - Only runs on pushes to `develop`
   - Deploys to staging environment

5. **Deploy Production**
   - Runs after successful build job
   - Only runs on pushes to `main`
   - Deploys to production environment

### Test Workflow (`.github/workflows/test.yml`)

This workflow focuses specifically on testing and runs on all feature branches as well.

#### Jobs:

1. **Test**
   - Runs unit tests
   - Runs API integration tests
   - Runs end-to-end tests
   - Generates and uploads coverage report

## Docker Images

The pipeline builds and tags Docker images with:

- Branch name
- Semantic version (when tagged)
- Short SHA hash

## Deployment Environments

The pipeline supports deployment to the following environments:

- **Staging**: Deployed from the `develop` branch
- **Production**: Deployed from the `main` branch

## Required Secrets

The following secrets need to be configured in GitHub:

- `DOCKER_HUB_USERNAME`: Docker Hub username for image pushes
- `DOCKER_HUB_ACCESS_TOKEN`: Docker Hub access token for authentication

## Local Development

For local development, you can use the pre-commit hooks to run the same linting checks that are used in the CI pipeline:

```bash
pip install pre-commit
pre-commit install
```

You can also run the CI tests locally using Docker Compose:

```bash
docker-compose -f docker-compose.ci.yml up --build
```