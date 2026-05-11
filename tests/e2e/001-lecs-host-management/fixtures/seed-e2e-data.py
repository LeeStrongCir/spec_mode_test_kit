#!/usr/bin/env python3
"""Seed E2E test data for LECS host management.

Reads lecs-host-states.json and creates test user accounts and host records
in the test database. Designed to run before E2E test execution.

Usage:
    python tests/e2e/001-lecs-host-management/fixtures/seed-e2e-data.py

    Options (via environment variables):
        DATABASE_URL:    SQLAlchemy database URL (default: sqlite:///./e2e-test.db)
        DATA_FILE:       Path to host states JSON (default: resolves lecs-host-states.json next to this script)
        DRY_RUN:         If set to "1", prints what would be created without inserting

Returns:
    Exit code 0 on success, 1 on failure.
    Prints success/failure status for each record.
"""

import json
import sys
import os
import uuid
from pathlib import Path

BACKEND_DIR = str(Path(__file__).resolve().parent.parent.parent.parent.parent / "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_FILE = SCRIPT_DIR / "data" / "lecs-host-states.json"
DATA_FILE = os.environ.get("DATA_FILE", str(DEFAULT_DATA_FILE))
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./e2e-test.db")
DRY_RUN = os.environ.get("DRY_RUN", "0") == "1"


def load_data(data_file: str) -> dict:
    """Load test data from JSON file."""
    path = Path(data_file)
    if not path.exists():
        print(f"ERROR: Data file not found: {path}")
        sys.exit(1)

    with open(path) as f:
        return json.load(f)


def seed_users(users: list[dict], session=None):
    """Create test user accounts."""
    print(f"\n{'=' * 50}")
    print(f"Seeding {len(users)} user(s) {'(DRY RUN)' if DRY_RUN else ''}")
    print(f"{'=' * 50}")

    created = 0
    for user in users:
        uid = user["id"]
        username = user["username"]
        email = user["email"]
        role = user["role"]

        if DRY_RUN:
            print(f"  [DRY] Would create user: {username} ({email}) [{role}]")
            created += 1
            continue

        if session is None:
            print(f"  [SKIP] No database session — user {username} not created")
            continue

        try:
            from app.models.user import User, Base
            from app.services.password_service import hash_password

            if session and not DRY_RUN:
                Base.metadata.create_all(bind=session.get_bind())

            existing = session.query(User).filter_by(username=username).first()
            if existing:
                print(f"  [SKIP] User {username} already exists")
            else:
                user_record = User(
                    id=uuid.UUID(str(uid)) if isinstance(uid, str) else uid,
                    username=username,
                    email=email,
                    password_hash=hash_password("E2eTest123!"),
                )
                session.add(user_record)
            print(f"  [OK]  Seeded user: {username}")
            created += 1
        except Exception as e:
            print(f"  [FAIL] Failed to create user {username}: {e}")

    print(f"\n  Users created: {created}/{len(users)}")
    return created


def seed_hosts(hosts: list[dict], session=None):
    """Create test host records."""
    print(f"\n{'=' * 50}")
    print(f"Seeding {len(hosts)} host(s) {'(DRY RUN)' if DRY_RUN else ''}")
    print(f"{'=' * 50}")

    created = 0
    for host in hosts:
        host_id = host["id"]
        hostname = host["hostname"]
        status = host["status"]
        spec_id = host["spec_id"]
        user_id = host["user_id"]
        scenario = host.get("scenario", "")

        if DRY_RUN:
            print(f"  [DRY] Would create host: {hostname} [{status}, {spec_id}] — {scenario}")
            created += 1
            continue

        if session is None:
            print(f"  [SKIP] No database session — host {hostname} not created")
            continue

        try:
            from app.models.lecs_host import LECSHost, Base

            host_uuid = uuid.UUID(str(host_id)) if isinstance(host_id, str) else host_id
            uid = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id

            existing = session.query(LECSHost).filter_by(id=host_uuid).first()
            if existing:
                print(f"  [SKIP] Host {hostname} already exists")
            else:
                host_record = LECSHost(
                    id=host_uuid,
                    user_id=uid,
                    hostname=hostname,
                    billing_mode=host["billing_mode"],
                    instance_type=host["instance_type"],
                    spec_id=spec_id,
                    vcpu=host["vcpu"],
                    ram_gb=host["ram_gb"],
                    system_disk_gb=host["system_disk_gb"],
                    os_image=host["os_image"],
                    ip_mode=host["ip_mode"],
                    ip_address=host["ip_address"],
                    ip_mask=host["ip_mask"],
                    status=host["status"],
                    error_msg=host.get("error_msg"),
                    duration=host.get("duration", 1),
                    unit_price=host.get("unit_price", 0),
                    cost_info=host.get("cost_info"),
                    username=host.get("username", "root"),
                    password_hash=host.get("password_hash", ""),
                    deleted_at=host.get("deleted_at"),
                )
                session.add(host_record)
            print(f"  [OK]  Seeded host: {hostname} [{status}]")
            created += 1
        except Exception as e:
            print(f"  [FAIL] Failed to create host {hostname}: {e}")

    print(f"\n  Hosts created: {created}/{len(hosts)}")
    return created


def main():
    """Main entry point for the seeding script."""
    print(f"LECS Host Management E2E Data Seeder")
    print(f"Data file: {DATA_FILE}")
    print(f"Database:  {DATABASE_URL}")
    print(f"Dry run:   {DRY_RUN}")

    data = load_data(DATA_FILE)
    users = data.get("users", [])
    hosts = data.get("hosts", [])

    if not users and not hosts:
        print("ERROR: No test data found in JSON file")
        sys.exit(1)

    session = None
    if not DRY_RUN:
        try:
            from sqlalchemy import create_engine
            from sqlalchemy.orm import Session

            engine = create_engine(DATABASE_URL, echo=False)
            session = Session(engine)
            print("\nDatabase connection established.")
        except ImportError:
            print("\nWARNING: Application models not importable — running in print-only mode")
            print("Set DATABASE_URL and ensure app code is on PYTHONPATH to seed real data.")
            session = None

    user_count = seed_users(users, session)
    host_count = seed_hosts(hosts, session)

    if session:
        try:
            session.commit()
            print(f"\n{'=' * 50}")
            print(f"Seeding complete: {user_count} users, {host_count} hosts")
            session.close()
        except Exception as e:
            session.rollback()
            print(f"\nSeeding failed — rolled back: {e}")
            sys.exit(1)
    else:
        print(f"\n{'=' * 50}")
        print(f"Preview complete: {user_count} users, {host_count} hosts would be created")

    sys.exit(0)


if __name__ == "__main__":
    main()
