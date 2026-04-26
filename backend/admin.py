#!/usr/bin/env python3
"""
Admin user management CLI — run from the backend/ directory.

Usage:
    python admin.py list                    # list all admin users
    python admin.py info <email>            # show user details
    python admin.py promote <email>         # promote user to admin
    python admin.py demote <email>          # demote admin to regular user
    python admin.py promote <email> --yes   # skip confirmation prompt
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)


def _db():
    from app.database import SessionLocal
    return SessionLocal()


def _get_user(db, email: str):
    from app.models.user import User
    return db.query(User).filter(User.email == email).first()


def _assert_table_exists():
    from sqlalchemy import inspect
    from app.database import engine
    if not inspect(engine).has_table("users"):
        print("Error: 'users' table not found. Run migrations first: python migrate.py upgrade")
        sys.exit(1)


def cmd_list():
    _assert_table_exists()
    from app.models.user import User, UserRole
    db = _db()
    try:
        admins = db.query(User).filter(User.role == UserRole.admin).order_by(User.id).all()
        if not admins:
            print("\n  No admin users found.\n")
            return
        print(f"\n  {'ID':<6} {'Email':<40} {'Username':<20} {'Active'}")
        print(f"  {'-'*6} {'-'*40} {'-'*20} {'-'*6}")
        for u in admins:
            active = "yes" if u.is_active else "no"
            print(f"  {u.id:<6} {u.email:<40} {u.username:<20} {active}")
        print()
    finally:
        db.close()


def cmd_info(email: str):
    _assert_table_exists()
    db = _db()
    try:
        u = _get_user(db, email)
        if not u:
            print(f"\n  Error: no user found with email '{email}'\n")
            sys.exit(1)
        print(f"\n  ID       : {u.id}")
        print(f"  Email    : {u.email}")
        print(f"  Username : {u.username}")
        print(f"  Role     : {u.role.value}")
        print(f"  Active   : {'yes' if u.is_active else 'no'}")
        print(f"  Provider : {u.sso_provider.value}")
        print(f"  Score    : {u.total_score}")
        print(f"  Joined   : {u.created_at.strftime('%Y-%m-%d %H:%M')}")
        print()
    finally:
        db.close()


def cmd_promote(email: str, yes: bool = False):
    _assert_table_exists()
    from app.models.user import UserRole
    db = _db()
    try:
        u = _get_user(db, email)
        if not u:
            print(f"\n  Error: no user found with email '{email}'\n")
            sys.exit(1)
        if u.role == UserRole.admin:
            print(f"\n  '{email}' is already an admin. Nothing to do.\n")
            return
        print(f"\n  User   : {u.username} ({u.email})")
        print(f"  Change : {u.role.value} → admin")
        if not yes:
            confirm = input("\n  Promote this user to admin? [y/N] ").strip().lower()
            if confirm != "y":
                print("  Aborted.\n")
                return
        u.role = UserRole.admin
        db.commit()
        print(f"  Done: '{email}' is now an admin ✓\n")
    finally:
        db.close()


def cmd_demote(email: str, yes: bool = False):
    _assert_table_exists()
    from app.models.user import User, UserRole
    db = _db()
    try:
        u = _get_user(db, email)
        if not u:
            print(f"\n  Error: no user found with email '{email}'\n")
            sys.exit(1)
        if u.role != UserRole.admin:
            print(f"\n  '{email}' is not an admin. Nothing to do.\n")
            return
        # Guard: refuse to demote the last admin
        admin_count = db.query(User).filter(User.role == UserRole.admin).count()
        if admin_count <= 1:
            print(f"\n  Error: '{email}' is the only admin. Cannot demote — you would lock yourself out.\n")
            sys.exit(1)
        print(f"\n  User   : {u.username} ({u.email})")
        print(f"  Change : admin → user")
        if not yes:
            confirm = input("\n  Demote this admin to regular user? [y/N] ").strip().lower()
            if confirm != "y":
                print("  Aborted.\n")
                return
        u.role = UserRole.user
        db.commit()
        print(f"  Done: '{email}' has been demoted to user ✓\n")
    finally:
        db.close()


def main():
    args = sys.argv[1:]
    yes = "--yes" in args
    args = [a for a in args if a != "--yes"]

    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0].lower()

    if cmd == "list":
        cmd_list()
    elif cmd == "info":
        if len(args) < 2:
            print("  Error: provide an email address, e.g. python admin.py info user@example.com\n")
            sys.exit(1)
        cmd_info(args[1])
    elif cmd == "promote":
        if len(args) < 2:
            print("  Error: provide an email address, e.g. python admin.py promote user@example.com\n")
            sys.exit(1)
        cmd_promote(args[1], yes=yes)
    elif cmd == "demote":
        if len(args) < 2:
            print("  Error: provide an email address, e.g. python admin.py demote user@example.com\n")
            sys.exit(1)
        cmd_demote(args[1], yes=yes)
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
