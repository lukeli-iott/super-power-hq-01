---
title: Super Power HQ
emoji: 🦸
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# Super Power HQ

A public hero registration and admin review system built with **Streamlit**. Aspiring heroes submit their details via a sign-up form; HQ staff review applications through a password-protected admin dashboard.

**Live on HuggingFace Spaces:** https://huggingface.co/spaces/uklukie/super-power-hq

<img width="858" height="601" alt="image" src="https://github.com/user-attachments/assets/9f4ea414-98a5-41d9-8649-cbc5d0e60449" />

<img width="1150" height="801" alt="image" src="https://github.com/user-attachments/assets/3d02f15c-66c0-42c7-b95b-3d41fd92d665" />

## Features

- **Public Sign-Up Form** — Heroes register with name, powers, age, location, and email. Server-side validation ensures data quality.
- **Admin Dashboard** — Password-protected interface to review all submitted applications with CSV export.
- **Real-time Data Persistence** — Submissions are stored in SQLite (heroes.db) and visible immediately in the admin view.
- **Responsive Design** — Built with Streamlit, works on desktop and mobile.
- **Easy Deployment** — Runs on HuggingFace Spaces free tier (no Docker needed).

## Navigation

Use the sidebar to switch between:
- **Sign Up** — Public hero registration form
- **Admin Review** — Password-protected admin dashboard

## Local Development

### Prerequisites

- Python 3.12+
- pip

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/lukeli-iott/super-power-hq-01.git
   cd super-power-hq
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Regenerate heroes.db from schema:
   ```bash
   sh build-db.sh
   ```

5. Set the admin password:
   ```bash
   export ADMIN_PASSWORD=your-secure-password
   ```

6. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

   The app will open in your browser at `http://localhost:8501`

### Testing Locally

1. **Run the app**:
   ```bash
   streamlit run app.py
   ```

2. **Test the Sign Up form**:
   - Go to the "Sign Up" tab (default)
   - Fill in all fields and submit
   - You should see a success message
   - Verify the data was saved: `sqlite3 heroes.db "SELECT * FROM submissions ORDER BY id DESC LIMIT 1;"`

3. **Test the Admin Dashboard**:
   - Click "Admin Review" in the sidebar
   - Try an incorrect password → should see error
   - Enter the correct password (value of `ADMIN_PASSWORD` env var) → should see all applications
   - Verify CSV download button works

4. **Test validation**:
   - Try submitting with empty fields → should show error messages
   - Try invalid email → should show error
   - Try age > 150 or non-numeric → should show error

5. **XSS protection**:
   - Try submitting with `<script>alert(1)</script>` as hero name
   - Form validation should reject it (no script tags in field)
   - Even if a malicious row exists in the database, Streamlit auto-escapes HTML

## Deployment to HuggingFace Spaces

The app is already deployed! Visit: **https://huggingface.co/spaces/lookiott/super-power-hq**

### How It Works

- **Platform:** HuggingFace Spaces (Pro plan with Docker support)
- **Backend:** Streamlit (Python web framework)
- **Containerization:** Docker (custom runtime with full control)
- **Storage:** SQLite bundled in Docker container
- The GitHub repo is synced to HuggingFace Spaces via automated CI/CD
- Every push to `main` triggers tests and then deploys to HF
- HF automatically builds the Docker image from `Dockerfile` and runs the app
- Pro plan enables Docker SDK and persistent deployments

### Setup for Your Own Space (if deploying elsewhere)

1. **Create a new HuggingFace Space**:
   - Go to [huggingface.co/spaces](https://huggingface.co/spaces)
   - Click "Create new Space"
   - Choose **Docker** as the SDK
   - Ensure you have a **Pro or higher plan** (Docker requires paid tier)
   - Name it (e.g., `super-power-hq`)

2. **Set the admin password**:
   - In your Space Settings → "Variables and secrets"
   - Add a secret `ADMIN_PASSWORD` (required for `/admin` access)
   - Save; the Space will rebuild with this environment variable

3. **Connect GitHub to HuggingFace**:
   ```bash
   git remote add space https://huggingface.co/spaces/<your-username>/<your-space-name>
   git push space main
   ```

4. **Access your Space**:
   - Main app: `https://huggingface.co/spaces/<your-username>/<your-space-name>`
   - Use sidebar to navigate between "Sign Up" and "Admin Review"
   - Admin review requires the password you set in secrets

## CI/CD & Automated Deployment

### GitHub Actions

One workflow is included in `.github/workflows/ci.yml`:

**`ci.yml` — Test & Deploy to HuggingFace Spaces**

Runs on every push to `main` and every pull request:
1. **Test stage** (all branches):
   - Sets up Python 3.12
   - Installs dependencies (Streamlit)
   - Validates Streamlit app syntax
   - Checks Streamlit config exists
   - Verifies database connectivity
2. **Deploy stage** (only on push to main):
   - Configures git credentials
   - Pushes to HuggingFace Space using stored `HF_TOKEN`
   - HF automatically detects `streamlit` in requirements.txt
   - HF Space auto-rebuilds and deploys

### Setup GitHub Actions

1. **Generate HuggingFace Token** (if deploying to your own Space):
   - Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
   - Create a new token with **write** access
   - Copy the token

2. **Add token to GitHub Secrets**:
   - Go to your GitHub repo: Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `HF_TOKEN`
   - Value: paste your HuggingFace token
   - Click "Add secret"

3. **Verify workflows**:
   - Go to your repo's "Actions" tab
   - You should see "CI & Deploy to HuggingFace"
   - Next push to `main` will trigger the workflow

### Workflow Details

**On every push to main:**
```
Tests run (Streamlit syntax, config, database)
  ↓
If all pass:
  ↓
Deploy to HuggingFace Space
  ↓
HF Space auto-rebuilds and redeploys live
```

**On pull requests:**
- Tests run to validate changes
- Deployment does NOT run (safe for PRs)
- Merge to main to trigger deployment

## 📊 Data Persistence (Pro Plan)

**Current setup (Docker + SQLite in container):**

- `heroes.db` is bundled into the Docker image
- Submissions persist **while the Space is running**
- Data is **lost when:**
  - The Space is stopped/restarted
  - You push a new commit (triggers rebuild)
  - HuggingFace performs maintenance

**For production use with full persistence:**

Option 1: **HuggingFace Persistent Storage**
- Mount a persistent volume in the Docker container
- Submissions survive restarts
- Requires additional HF Space storage

Option 2: **External Database**
- PostgreSQL on Supabase, Railway, or similar
- Full persistence + backup capabilities
- Can be accessed from anywhere

Option 3: **Regular Backups**
- Export submissions as CSV from admin dashboard
- Schedule periodic manual backups

**Current recommendation:** Use Option 1 (HF persistent storage) for production, or periodically export CSV backups.

## Database Schema

The `submissions` table has the following columns:

| Column | Type | Notes |
|--------|------|-------|
| `id` | INTEGER | Primary key, auto-incremented |
| `hero_name` | TEXT | Required, max 200 chars |
| `powers` | TEXT | Required, max 500 chars |
| `age` | TEXT | Required, digits only, 1–150 |
| `location` | TEXT | Required, max 200 chars |
| `email` | TEXT | Required, valid email format, max 200 chars |

### Regenerating the Database

The `heroes.db` file is pre-built and committed to the repository. To regenerate it from scratch:

```bash
sh build-db.sh
```

This will:
1. Drop the existing `heroes.db`
2. Load the schema from `schema.sql`
3. Seed with test data from `seed.sql`

## Architecture

- **Framework**: Streamlit (Python) — simple, no-backend-needed web framework
- **Database**: SQLite (stdlib) — lightweight, file-based storage
- **Hosting**: HuggingFace Spaces free tier (Streamlit SDK)
- **Auth**: Simple password check in Streamlit session state
- **Security**: 
  - Parameterized SQL queries (no SQL injection)
  - Streamlit's built-in HTML escaping (no XSS)
  - Password stored as environment variable (never in code)

## File Structure

```
super-power-hq/
├── app.py                 # Streamlit app (sign-up form, admin dashboard)
├── requirements.txt       # Python dependencies (streamlit only)
├── .streamlit/
│   └── config.toml        # Streamlit configuration
├── .github/workflows/
│   └── ci.yml             # GitHub Actions CI/CD (test & deploy to HF)
├── .gitignore             # Git ignore rules
├── README.md              # This file
├── schema.sql             # Database schema (source of truth)
├── seed.sql               # Test data
├── build-db.sh            # Script to regenerate heroes.db
└── heroes.db              # SQLite database (committed to repo)
```

## Security Notes

- **SQL Injection**: All database queries use parameterized statements (`?` placeholders).
- **XSS**: Jinja2 autoescaping is enabled by default; all user input is HTML-escaped.
- **Admin Auth**: HTTP Basic Auth with timing-safe password comparison; password never committed to source code.
- **Validation**: Server-side validation on sign-up form (required fields, email format, age range).

## Contributing

To make changes:

1. Create a branch: `git checkout -b feature/my-feature`
2. Make changes and commit: `git commit -m "Add my feature"`
3. Push: `git push origin feature/my-feature`
4. Create a pull request on GitHub

## Troubleshooting

### Admin dashboard shows "Incorrect password"
Ensure `ADMIN_PASSWORD` is set as:
- A GitHub Secret (if using CI/CD to HF)
- An environment variable `ADMIN_PASSWORD=your-password` (for local testing)
- A Space Secret (in HuggingFace Space Settings → Variables and secrets)

### Sign-up form shows validation errors
Check the error message. Common issues:
- Missing a required field
- Email doesn't match `user@domain.tld` format
- Age is not a number or outside 1–150 range
- Text too long (max: hero_name 200 chars, powers 500 chars, email 200 chars, location 200 chars)

### Streamlit app won't start locally
- Ensure Python 3.12+ is installed
- Verify Streamlit is installed: `pip list | grep streamlit`
- Try: `streamlit run app.py --logger.level=debug`

### `database is locked` error
Rare with Streamlit (only one server process). If it occurs:
- Restart the Streamlit app
- Check if another terminal is accessing the database
- The app uses `PRAGMA busy_timeout = 5000` to wait on locks

### Submissions disappear after Space restart (HF Spaces)
Expected behavior due to ephemeral storage (see warning below). All data is lost when the Space sleeps or restarts. This is acceptable for a demo/free tier.

## License

Created for Super Power HQ recruitment demo. Feel free to adapt for your own use.
