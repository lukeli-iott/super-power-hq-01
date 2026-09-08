# GitHub Actions CI/CD Setup (Streamlit Edition)

This guide explains how to set up automated testing and deployment to HuggingFace Spaces using Streamlit.

## What's Included

One GitHub Actions workflow is in `.github/workflows/`:

**`ci.yml`** — Main CI/CD pipeline
- Runs tests on every push and pull request
- Deploys to HuggingFace Spaces on successful push to `main`
- HuggingFace automatically detects Streamlit and builds the app (no Docker needed)

## Prerequisites

### 1. GitHub Repository Setup

Your repo should already be set up at:
```
https://github.com/lukeli-iott/super-power-hq-01/
```

### 2. HuggingFace Space

Your Space should already exist at:
```
https://huggingface.co/spaces/iott-demo/super-power-hq
```

### 3. HuggingFace Access Token (REQUIRED)

You need to create a **write-access** token on HuggingFace:

1. Go to: https://huggingface.co/settings/tokens
2. Click "New token"
3. Name it (e.g., "GitHub Actions")
4. Set permission to **Write** (required for pushing to Spaces)
5. Click "Generate"
6. Copy the token (it won't be shown again!)

## Setup Steps

### Step 1: Add HF_TOKEN to GitHub Secrets

1. Go to your GitHub repo: **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Fill in:
   - **Name:** `HF_TOKEN`
   - **Secret:** Paste your HuggingFace token
4. Click **"Add secret"**

### Step 2: Verify Workflows

1. Go to your repo's **Actions** tab
2. You should see two workflows:
   - "CI & Deploy to HuggingFace"
   - "Docker Build Verification"
3. Both should show as enabled (green checkmark)

### Step 3: Test the Workflow

Make a small change and push to `main`:

```bash
# Example: make a minor change to README or add a comment
git add .
git commit -m "Test CI workflow"
git push origin main
```

Then:
1. Go to **Actions** tab on GitHub
2. Watch the workflows run
3. Check the logs for success/failure
4. Once deployment completes, HuggingFace Space should rebuild automatically

## Workflow Behavior

### On Push to Main

```
1. Tests run:
   ├─ Streamlit app syntax validation
   ├─ Streamlit config check
   └─ Database connectivity verification
   
2. If all tests pass → Deploy stage starts
   ├─ Configure git credentials
   ├─ Add HF Space remote with auth token
   └─ Push code to HF Space
   
3. HuggingFace Space auto-rebuilds:
   ├─ Downloads code from git
   ├─ Detects Streamlit in requirements.txt
   ├─ Builds Streamlit environment
   └─ Deploys app live (usually 1-5 minutes)
```

### On Pull Request

```
1. Tests run (same as above)
2. Deployment is SKIPPED (safe for PRs)
3. Merge to main to trigger deployment
```

## Monitoring & Troubleshooting

### Check Workflow Runs

1. Go to repo **Actions** tab
2. Click on a workflow run to see details
3. Click on a job (e.g., "test" or "deploy") to see logs

### Common Issues

#### ❌ "401 Unauthorized" on deploy
- **Cause:** `HF_TOKEN` is invalid, expired, or has insufficient permissions
- **Fix:** 
  1. Generate a new token at https://huggingface.co/settings/tokens (make sure it's **Write** access)
  2. Update the secret in GitHub (Settings → Secrets → update `HF_TOKEN`)

#### ❌ "Failed to push" or "repository not found"
- **Cause:** Space URL is incorrect or token doesn't have access to that Space
- **Fix:** Verify the Space URL in the workflow matches your actual Space:
  ```yaml
  # .github/workflows/ci.yml line ~45
  git remote add space https://huggingface.co/spaces/iott-demo/super-power-hq
  ```

#### ❌ "Database locked" in tests
- **Cause:** Database is in use by another process
- **Fix:** Stop any running Flask servers and re-run the workflow

#### ❌ Tests pass but deployment doesn't run
- **Cause:** Workflow only deploys on push to `main`, not pull requests
- **Fix:** Merge your PR to `main` to trigger deployment

### View HuggingFace Space Rebuild

After deployment succeeds:
1. Go to your Space: https://huggingface.co/spaces/iott-demo/super-power-hq
2. Click the "Logs" or "App" tab
3. Wait for the Space to rebuild (usually 1–5 minutes)
4. Once green, the new version is live

## Manual Deployment (if needed)

If workflows fail or you need to push manually:

```bash
# Add HF remote (one-time setup)
git remote add space https://oauth2:YOUR_HF_TOKEN@huggingface.co/spaces/iott-demo/super-power-hq

# Push to HF Space
git push space main
```

Replace `YOUR_HF_TOKEN` with your actual token.

## Customization

### Disable Deployment

If you want tests to run but NOT auto-deploy:

Edit `.github/workflows/ci.yml` and remove the `deploy` job or change the `if` condition:

```yaml
  deploy:
    if: false  # Disable deployment
```

### Change Trigger Branch

To deploy on branch other than `main`, edit `.github/workflows/ci.yml`:

```yaml
    if: github.event_name == 'push' && github.ref == 'refs/heads/your-branch-name'
```

### Add More Tests

Edit `.github/workflows/ci.yml` and add steps under the `test` job. Examples:

```yaml
      - name: Run Python linting
        run: |
          pip install flake8
          flake8 app.py --max-line-length=100
          
      - name: Check database schema
        run: |
          sqlite3 heroes.db ".schema submissions"
```

## Security Notes

- **Never commit secrets** — use GitHub Secrets, not env files
- **Token permission:** Use minimum necessary (Write for HF Space, not full account access)
- **Rotate tokens regularly** — regenerate HF token periodically
- **PR reviews:** Even with automation, review changes before merging to `main`

## Next Steps

1. ✅ Generate HF token (if not already done)
2. ✅ Add `HF_TOKEN` to GitHub Secrets
3. ✅ Push a test commit to trigger workflows
4. ✅ Monitor the workflow run in Actions tab
5. ✅ Verify deployment to HF Space

Once set up, every push to `main` will automatically test and deploy! 🚀
