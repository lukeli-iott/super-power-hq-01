# Streamlit Migration (HuggingFace Free Tier Support)

## What Changed

The app has been **converted from Flask to Streamlit** to support HuggingFace free tier (which doesn't include Docker).

### Files Modified:
- **app.py** — Rewritten for Streamlit instead of Flask
- **requirements.txt** — Now only requires Streamlit (removed Flask, Gunicorn)
- **README.md** — Updated with Streamlit instructions
- **.github/workflows/ci.yml** — Updated to test Streamlit app instead of Flask
- **.github/workflows/docker-build.yml** — Removed (Docker no longer needed)
- **CI_SETUP.md** — Updated with Streamlit-specific guidance

### Files Added:
- **.streamlit/config.toml** — Streamlit configuration (theme, UI settings)

### Files Kept Unchanged:
- **heroes.db**, **schema.sql**, **seed.sql**, **build-db.sh** — Database files unchanged
- **.gitignore** — Still valid
- All other infrastructure remains the same

## Key Differences: Flask vs Streamlit

| Feature | Flask | Streamlit |
|---------|-------|-----------|
| Server | Yes (Gunicorn needed) | Built-in (streamlit run) |
| HTML/CSS/JS | Required | Not needed (built-in UI) |
| Routing | Manual routes (@app.route) | Page-based (Streamlit manages) |
| Forms | Manual HTML forms | st.form() with widgets |
| Admin Auth | HTTP Basic Auth | Session state + password check |
| Database | sqlite3 direct | sqlite3 direct (same) |
| Hosting | Docker required | Streamlit SDK (HF free tier) |

## Local Development

### Before (Flask):
```bash
export ADMIN_PASSWORD=your-password
flask --app app run --debug
# Visit http://localhost:5000
```

### Now (Streamlit):
```bash
export ADMIN_PASSWORD=your-password
streamlit run app.py
# Automatically opens browser at http://localhost:8501
```

## HuggingFace Deployment

### Before (Docker):
1. Create Space with **Docker** SDK
2. Push to `space` remote
3. HF builds Docker image (slow, limited storage)

### Now (Streamlit):
1. Create Space with **Streamlit** SDK (not Docker)
2. Push to `space` remote
3. HF automatically runs Streamlit (faster, no Docker size limits)

## What's the Same?

- ✅ Database structure and data
- ✅ Form validation logic
- ✅ Admin authentication (password-based)
- ✅ SQL queries and security (parameterized, no injection)
- ✅ XSS protection (auto-escaped)
- ✅ GitHub + HuggingFace CI/CD workflow
- ✅ CSV export functionality (new feature!)

## What's Better?

- ✅ Runs on HF free tier (no Docker)
- ✅ Faster builds on HuggingFace
- ✅ No static files needed (CSS built into Streamlit)
- ✅ Less code overall (Streamlit handles UI)
- ✅ Admin panel accessible via sidebar (cleaner UX)
- ✅ CSV download button for data export

## Testing

### Local:
```bash
# Terminal 1: Start the app
streamlit run app.py

# Terminal 2: Quick smoke test
export ADMIN_PASSWORD=testpass
curl http://localhost:8501  # Should load the page
```

### HuggingFace:
1. Ensure `ADMIN_PASSWORD` is set in Space Settings → Secrets
2. Push to `space` remote
3. Wait for Space to build
4. Visit https://huggingface.co/spaces/iott-demo/svuper-power-hq
5. Test sign-up and admin panel

## Rollback (if needed)

To go back to Flask:
1. `git log --oneline` to find the last Flask commit
2. `git revert <commit-hash>`
3. Update README.md with Flask instructions
4. Manually re-add Dockerfile and templates/

**But Streamlit is recommended for HF free tier!**

## FAQ

**Q: Will existing database data be lost?**
A: No! `heroes.db` is unchanged and committed to git.

**Q: Can I still deploy to other platforms?**
A: Yes! Streamlit runs anywhere Python runs (Render, Railway, etc.). The migration doesn't lock you to HF.

**Q: Is the app less secure now?**
A: No! Security is the same:
- Parameterized SQL (no injection)
- Streamlit auto-escapes HTML (no XSS)
- Password stored in environment variables (not in code)

**Q: How do I customize the UI?**
A: Use `.streamlit/config.toml` for theme/colors. For more control, edit `app.py` and use Streamlit widgets.

**Q: Can I add more pages/routes?**
A: Yes! Use `st.sidebar.radio()` or `st.navigation()` to add pages.

## Next Steps

1. ✅ Code is ready to push
2. Make sure `ADMIN_PASSWORD` secret is in GitHub (Settings → Secrets)
3. Push to GitHub: `git push origin main`
4. GitHub Actions will test and deploy automatically
5. Watch the deployment in the "Actions" tab
6. Once HF Space finishes building, visit the live app!

---

**Questions?** Check README.md or CI_SETUP.md for more details.
