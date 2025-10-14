#!/usr/bin/env python3
"""
Database migration: Add additional Netmiko parameters to devices table

This migration adds the following columns to the devices table:
- global_delay_factor: Multiplier for all delays (default 1)
- fast_cli: Disable delays for faster execution (default False)
- conn_timeout: TCP connection timeout (default 10)
- auth_timeout: Authentication timeout (default None)
- banner_timeout: Banner timeout (default 15)
- read_timeout_override: Override read timeout (default None)
- keepalive: Keepalive interval in seconds (default 0)

Run this migration if you have an existing database before upgrading to the new version.
If you're starting with a fresh database, this migration is not needed.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import engine
from app.config import settings


async def migrate():
    """Add new columns to devices table"""
    print("Starting migration: Add Netmiko parameters to devices table")
    print(f"Database: {settings.database_url}")

    async with engine.begin() as conn:
        # Check if columns already exist
        print("\nChecking existing columns...")
        result = await conn.execute(
            text("SELECT sql FROM sqlite_master WHERE type='table' AND name='devices'")
        )
        table_schema = result.scalar_one_or_none()

        if not table_schema:
            print("❌ Error: Devices table not found!")
            return False

        print(f"Current schema: {table_schema[:100]}...")

        # Add columns if they don't exist
        columns_to_add = [
            ("global_delay_factor", "INTEGER DEFAULT 1 NOT NULL"),
            ("fast_cli", "BOOLEAN DEFAULT 0 NOT NULL"),
            ("conn_timeout", "INTEGER DEFAULT 10 NOT NULL"),
            ("auth_timeout", "INTEGER"),
            ("banner_timeout", "INTEGER DEFAULT 15 NOT NULL"),
            ("read_timeout_override", "INTEGER"),
            ("keepalive", "INTEGER DEFAULT 0 NOT NULL"),
        ]

        for column_name, column_def in columns_to_add:
            if column_name not in table_schema:
                print(f"\n✓ Adding column: {column_name}")
                try:
                    await conn.execute(
                        text(f"ALTER TABLE devices ADD COLUMN {column_name} {column_def}")
                    )
                    print(f"  ✓ Column '{column_name}' added successfully")
                except Exception as e:
                    print(f"  ⚠ Warning: Could not add column '{column_name}': {e}")
            else:
                print(f"  ⊙ Column '{column_name}' already exists, skipping")

        print("\n✓ Migration completed successfully!")
        return True


async def verify():
    """Verify migration was successful"""
    print("\nVerifying migration...")

    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT sql FROM sqlite_master WHERE type='table' AND name='devices'")
        )
        table_schema = result.scalar_one()

        required_columns = [
            "global_delay_factor",
            "fast_cli",
            "conn_timeout",
            "auth_timeout",
            "banner_timeout",
            "read_timeout_override",
            "keepalive",
        ]

        missing_columns = [col for col in required_columns if col not in table_schema]

        if missing_columns:
            print(f"⚠ Warning: Some columns are still missing: {missing_columns}")
            return False
        else:
            print("✓ All columns verified!")
            print("\nNew table schema:")
            print(table_schema)
            return True


async def rollback():
    """Rollback migration (remove added columns)"""
    print("\n⚠ Rolling back migration...")
    print("SQLite does not support DROP COLUMN directly.")
    print("To rollback, you need to:")
    print("1. Backup your data")
    print("2. Drop the devices table")
    print("3. Recreate with old schema")
    print("4. Restore your data")
    return False


async def main():
    """Main migration runner"""
    print("=" * 70)
    print("Database Migration: Add Netmiko Parameters")
    print("=" * 70)

    if len(sys.argv) > 1 and sys.argv[1] == "--rollback":
        await rollback()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        await verify()
        return

    # Run migration
    success = await migrate()

    if success:
        await verify()
        print("\n" + "=" * 70)
        print("Migration completed successfully!")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("Migration failed!")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
