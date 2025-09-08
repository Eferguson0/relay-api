#!/usr/bin/env python3
"""
Database reset script for development.
This script wipes the database and creates a fresh migration.
"""

import subprocess
import sys
from pathlib import Path

from sqlalchemy import text

from app.db.session import engine

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_command(cmd: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completed")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"   Error: {e.stderr.strip()}")
        return False


def wipe_database():
    """Drop all tables from the database."""
    print("🗑️  Wiping database...")
    try:
        with engine.connect() as conn:
            # Get all table names dynamically
            result = conn.execute(
                text(
                    """
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
            """
                )
            )
            tables = [row[0] for row in result.fetchall()]

            # Drop all tables
            for table in tables:
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))

            # Get all enum types dynamically
            result = conn.execute(
                text(
                    """
                SELECT typname 
                FROM pg_type 
                WHERE typtype = 'e' AND typnamespace = (
                    SELECT oid FROM pg_namespace WHERE nspname = 'public'
                )
            """
                )
            )
            enum_types = [row[0] for row in result.fetchall()]

            # Drop all enum types
            for enum_type in enum_types:
                conn.execute(text(f"DROP TYPE IF EXISTS {enum_type} CASCADE"))

            conn.commit()
            print("✅ Database wiped successfully")
            return True
    except Exception as e:
        print(f"❌ Failed to wipe database: {e}")
        return False


def remove_migrations():
    """Remove all existing migration files."""
    print("🗑️  Removing existing migrations...")
    try:
        migrations_dir = project_root / "alembic" / "versions"
        if migrations_dir.exists():
            for migration_file in migrations_dir.glob("*.py"):
                if migration_file.name != "__init__.py":
                    migration_file.unlink()
                    print(f"   Removed: {migration_file.name}")
        print("✅ Migrations removed successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to remove migrations: {e}")
        return False


def create_fresh_migration():
    """Create a fresh initial migration."""
    migration_name = "initial_migration"
    cmd = f"uv run alembic revision --autogenerate -m '{migration_name}'"
    return run_command(cmd, "Creating fresh migration")


def apply_migration():
    """Apply the migration to the database."""
    cmd = "uv run alembic upgrade head"
    return run_command(cmd, "Applying migration")


def create_initial_users():
    """Create initial admin and test users."""
    print("👤 Creating initial users...")
    try:
        from app.core.rid import generate_rid
        from app.db.session import SessionLocal
        from app.models.auth.user import AuthUser
        from app.services.auth_service import get_password_hash

        db = SessionLocal()
        try:
            # Create admin user
            admin_user = AuthUser(
                id=generate_rid("auth", "user"),
                email="admin@example.com",
                hashed_password=get_password_hash("admin"),
                full_name="Admin User",
                is_superuser=True,
                is_active=True,
            )
            db.add(admin_user)

            # Create test user
            test_user = AuthUser(
                id=generate_rid("auth", "user"),
                email="test@gmail.com",
                hashed_password=get_password_hash("test123"),
                full_name="Test User",
                is_superuser=False,
                is_active=True,
            )
            db.add(test_user)

            db.commit()
            print("✅ Initial users created successfully")

            # Show created users
            users = db.query(AuthUser).all()
            print(f"📊 Created {len(users)} users:")
            for user in users:
                print(f"   - ID: {user.id}, Email: {user.email}")

            return True
        finally:
            db.close()
    except Exception as e:
        print(f"❌ Failed to create initial users: {e}")
        return False


def main():
    """Main function to reset database and create fresh migration."""
    print("🚀 Starting database reset process...")
    print("=" * 50)

    steps = [
        ("Wiping database", wipe_database),
        ("Removing existing migrations", remove_migrations),
        ("Creating fresh migration", create_fresh_migration),
        ("Applying migration", apply_migration),
        ("Creating initial users", create_initial_users),
    ]

    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Database reset failed at step: {step_name}")
            sys.exit(1)
        print()

    print("=" * 50)
    print("🎉 Database reset completed successfully!")
    print("\n📋 Summary:")
    print("   - Database wiped clean")
    print("   - Fresh migration created and applied")
    print("   - Initial users created")
    print("\n🔑 Test credentials:")
    print("   - Admin: admin@example.com / admin")
    print("   - Test: test@gmail.com / test123")


if __name__ == "__main__":
    main()
