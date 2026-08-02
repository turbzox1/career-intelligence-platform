#!/usr/bin/env python
"""Seed the database with master skills, demo jobs and a demo admin user.

Usage:
    python scripts/seed.py [--email admin@careerintel.io] [--password Admin123!]
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

from app.db.seed import seed_admin, seed_all
from app.db.session import SessionLocal


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed database fixtures")
    parser.add_argument("--email", default="admin@careerintel.io")
    parser.add_argument("--password", default="Admin123!")
    parser.add_argument("--admin", action="store_true", help="also create the demo admin user")
    args = parser.parse_args()

    with SessionLocal() as db:
        counts = seed_all(db)
        print(f"Seeded: {counts}")
        if args.admin:
            user = seed_admin(db, email=args.email, password=args.password)
            print(f"Admin ready: {user.email}")


if __name__ == "__main__":
    main()
