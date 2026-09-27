# Railway Deployment Guide

## Backend Setup with Persistent Storage

### 1. Configure Database Path

The backend now uses an environment variable for the database location:

```
DATABASE_URL=sqlite:////data/wilsonic.db
```

**Important notes:**
- **4 slashes** after `sqlite:` for absolute paths (`sqlite:////data/...`)
- **3 slashes** for relative paths (`sqlite:///./wilsonic.db`)
- The `/data` path should match your Railway Volume mount point

### 2. Attach Railway Volume

1. In your Railway backend service, go to **Settings > Volumes**
2. Click **New Volume**
3. Set mount path: `/data`
4. Volume size: 1GB (sufficient for SQLite database)
5. Click **Add Volume**

### 3. Set Environment Variable

In your Railway backend service **Variables** section:

```
DATABASE_URL=sqlite:////data/wilsonic.db
```

**Critical**: Use 4 slashes (`////`) because `/data/wilsonic.db` is an absolute path.

### 4. Redeploy

After adding the volume and environment variable, trigger a redeploy. The app will now:
- Store the SQLite database at `/data/wilsonic.db` (persisted across deploys)
- Create tables automatically on first startup if database is empty

---

## Importing Historical Data (299,873 records)

You have **two options** for importing the historical data:

### Option A: Railway Shell/Console (Recommended)

1. **Upload Excel file to a publicly accessible URL** (Google Drive, Dropbox, etc.)
   - Make sure the link is a direct download link (not a preview page)

2. **Open Railway Shell** for your backend service:
   - Railway Dashboard → Your Service → **Shell** tab (or **Connect** button)

3. **Run the import script:**
   ```bash
   python -m backend.import_from_url https://your-url-here/historical_draws.xlsx
   ```

4. **Monitor progress** - the script will:
   - Download the file
   - Clear any existing draws
   - Insert 299,873+ historical records in batches
   - Report progress every 10,000 rows
   - Verify frequencies match expected distribution

5. **Completion** - once done, the data is persisted in `/data/wilsonic.db`

### Option B: Temporary API Endpoint (If Railway Shell unavailable)

If Railway doesn't provide shell access, I can create a temporary admin API endpoint that:
- Accepts the Excel file URL
- Runs the import in the background
- Returns import status

**Let me know if you need this approach.**

---

## Verifying the Import

After importing, check the API:

```bash
curl https://wilsonic-production.up.railway.app/stats/summary
```

You should see:
```json
{
  "total_draws": 299873,
  "letter_counts": {
    "A": ~114500,
    "B": ~63300,
    ...
  }
}
```

---

## Database Backup (Optional)

To backup your Railway database:

1. Open Railway Shell
2. Run: `cat /data/wilsonic.db > backup.db`
3. Download `backup.db` from the shell
4. Or use Railway's Volume backup feature (if available)

---

## Troubleshooting

### "Database is locked" error
- SQLite is single-writer - if Railway runs multiple instances, you may see lock errors
- Solution: Ensure Railway runs only 1 replica for SQLite backend
- Better solution: Migrate to PostgreSQL for production (using Railway's Postgres addon)

### Import script fails with "ModuleNotFoundError"
- Ensure you're running from the project root: `python -m backend.import_from_url ...`
- The Railway shell should automatically be in the correct directory

### Database file not persisting
- Verify the volume is mounted at `/data`
- Check `DATABASE_URL` has 4 slashes: `sqlite:////data/wilsonic.db`
- Check Railway logs for database path being used at startup
