# CI and Deployment

The GitHub Actions workflow in `.github/workflows/ci.yml` runs Ruff, compiles the Flask app and tests, and runs the test suite on pushes and pull requests. On pushes to `main`, it also pushes the repository to the configured Hugging Face Space.

## Hugging Face deployment

The deployment job uses the `HF_TOKEN` GitHub Actions secret and pushes to `uklukie/super-power-hq`. Update the Space URL in `.github/workflows/ci.yml` if you deploy to a different Space. The Space should use the repository's Dockerfile.

Set `ADMIN_PASSWORD` and `SECRET_KEY` in the Space's environment. Set `DATABASE_URL` to a persistent PostgreSQL database if submissions must survive container replacement.

## Vercel deployment

Vercel deployment is managed through the Vercel project connected to this repository. Configure `DATABASE_URL`, `ADMIN_PASSWORD`, and `SECRET_KEY` in the Vercel project's environment variables. See [README.md](README.md#deploy-to-vercel) for setup details. Vercel does not use the Hugging Face token or the GitHub Actions deployment job.
