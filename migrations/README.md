# Database Migrations

This directory contains database migration scripts for schema updates.

## Available Migrations

### add_netmiko_parameters.py

Adds additional Netmiko ConnectHandler parameters to the `devices` table:
- `global_delay_factor`: Multiplier for all delays (default 1)
- `fast_cli`: Disable delays for faster execution (default False)
- `conn_timeout`: TCP connection timeout (default 10)
- `auth_timeout`: Authentication timeout (default None)
- `banner_timeout`: Banner timeout (default 15)
- `read_timeout_override`: Override read timeout (default None)
- `keepalive`: Keepalive interval in seconds (default 0)

## When to Run Migrations

- **Fresh Installation**: No migration needed. New databases will have all columns automatically.
- **Existing Installation**: Run migrations when upgrading to a version with schema changes.

## Running Migrations

### Option 1: Inside Docker Container

```bash
# Access the container
docker exec -it network-api-gateway bash

# Run the migration
python migrations/add_netmiko_parameters.py

# Verify the migration
python migrations/add_netmiko_parameters.py --verify
```

### Option 2: Direct Python (if running without Docker)

```bash
# Make sure you're in the project root
cd /path/to/network_cli_to_openapi

# Run the migration
python migrations/add_netmiko_parameters.py

# Verify the migration
python migrations/add_netmiko_parameters.py --verify
```

## Migration Output

Successful migration output:
```
======================================================================
Database Migration: Add Netmiko Parameters
======================================================================
Starting migration: Add Netmiko parameters to devices table
Database: sqlite+aiosqlite:///./data/network_gateway.db

Checking existing columns...
Current schema: CREATE TABLE devices (...)...

✓ Adding column: global_delay_factor
  ✓ Column 'global_delay_factor' added successfully
✓ Adding column: fast_cli
  ✓ Column 'fast_cli' added successfully
...

✓ Migration completed successfully!

Verifying migration...
✓ All columns verified!
======================================================================
Migration completed successfully!
======================================================================
```

## Backup Recommendation

**Always backup your database before running migrations:**

```bash
# Backup database
cp data/network_gateway.db data/network_gateway.db.backup.$(date +%Y%m%d_%H%M%S)

# Run migration
python migrations/add_netmiko_parameters.py

# If something goes wrong, restore backup
cp data/network_gateway.db.backup.YYYYMMDD_HHMMSS data/network_gateway.db
```

## Troubleshooting

### "Column already exists" warnings

This is normal if you've already run the migration. The script will skip existing columns.

### Migration fails

1. Check database file exists: `ls -l data/network_gateway.db`
2. Check database permissions
3. Restore from backup if needed
4. Check logs for specific error messages

### SQLite limitations

SQLite does not support all ALTER TABLE operations. This migration uses `ADD COLUMN` which is supported. If you need to modify existing columns, you'll need to:
1. Create a new table with the new schema
2. Copy data from old table
3. Drop old table
4. Rename new table

## Creating New Migrations

When adding new features that require schema changes:

1. Create a new migration script in this directory
2. Use descriptive names: `add_feature_name.py`
3. Include verification logic
4. Update this README with migration details
5. Test on a backup database first
