# Data Directory

This directory is used for persistent application data storage.

## Contents

- **`network_gateway.db`** - SQLite database file (created automatically on first run)

## Important Notes

- This directory is **excluded from git** (see `.gitignore`)
- The database file is created automatically when the application starts
- Data in this directory persists across container restarts
- Back up this directory regularly in production environments

## Fresh Installation

On a fresh installation, this directory will be empty. The application will automatically:

1. Create `network_gateway.db` on first startup
2. Initialize the database schema
3. Create the default admin user (username: `admin`, password: `changeme`)

## Backup

To backup your data:

```bash
# Backup the entire data directory
tar -czf backup_$(date +%Y%m%d).tar.gz data/

# Or just the database
cp data/network_gateway.db backup_$(date +%Y%m%d).db
```

See [DEPLOYMENT.md](../DEPLOYMENT.md) for automated backup scripts.
