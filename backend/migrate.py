#!/usr/bin/env python3
"""
Migration CLI — run from the backend/ directory.

Usage:
    python migrate.py                 # show status
    python migrate.py upgrade         # apply all pending migrations (default)
    python migrate.py upgrade <rev>   # apply up to a specific revision
    python migrate.py downgrade -1    # roll back one step
    python migrate.py downgrade <rev> # roll back to a specific revision
    python migrate.py create <msg>    # generate a new migration file
    python migrate.py history         # show full migration history
    python migrate.py check           # assert no unapplied migrations (use in CI)
"""
import sys
import os
from alembic.config import Config
from alembic import command
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _alembic_cfg() -> Config:
    cfg = Config(os.path.join(BASE_DIR, "alembic.ini"))
    cfg.set_main_option("script_location", os.path.join(BASE_DIR, "alembic"))
    # Always source DATABASE_URL from the environment — never from alembic.ini
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        # Fall back to app config so local .env still works
        from app.config import settings
        db_url = settings.DATABASE_URL
    cfg.set_main_option("sqlalchemy.url", db_url)
    return cfg


def _current_heads(db_url: str) -> set[str]:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        ctx = MigrationContext.configure(conn)
        return ctx.get_current_heads()


def _pending(cfg: Config, db_url: str) -> list:
    script = ScriptDirectory.from_config(cfg)
    current = _current_heads(db_url)
    return [r for r in script.walk_revisions() if r.revision not in current and r.revision]


def cmd_status():
    cfg = _alembic_cfg()
    db_url = cfg.get_main_option("sqlalchemy.url")
    script = ScriptDirectory.from_config(cfg)
    current = _current_heads(db_url)
    head = set(script.get_heads())

    print(f"\n  Database : {_safe_url(db_url)}")
    print(f"  Current  : {', '.join(current) if current else '(no migrations applied)'}")
    print(f"  Head     : {', '.join(head)}")

    if current == head:
        print("  Status   : up to date ✓\n")
    else:
        pending = _pending(cfg, db_url)
        print(f"  Status   : {len(pending)} unapplied migration(s) pending\n")


def cmd_upgrade(revision: str = "head"):
    cfg = _alembic_cfg()
    db_url = cfg.get_main_option("sqlalchemy.url")
    _assert_db_reachable(db_url)
    print(f"\n  Upgrading to: {revision}")
    command.upgrade(cfg, revision)
    print("  Done ✓\n")


def cmd_downgrade(revision: str):
    cfg = _alembic_cfg()
    db_url = cfg.get_main_option("sqlalchemy.url")
    _assert_db_reachable(db_url)
    print(f"\n  Downgrading to: {revision}")
    command.downgrade(cfg, revision)
    print("  Done ✓\n")


def cmd_create(message: str):
    if not message:
        print("  Error: provide a message, e.g. python migrate.py create add_user_avatar\n")
        sys.exit(1)
    cfg = _alembic_cfg()
    command.revision(cfg, message=message, autogenerate=True)
    print("  Migration file created — review it before committing.\n")


def cmd_history():
    cfg = _alembic_cfg()
    command.history(cfg, verbose=False)


def cmd_check():
    """Exit 1 if there are unapplied migrations — safe to run in CI."""
    cfg = _alembic_cfg()
    db_url = cfg.get_main_option("sqlalchemy.url")
    _assert_db_reachable(db_url)
    pending = _pending(cfg, db_url)
    if pending:
        revs = [r.revision for r in pending]
        print(f"\n  FAIL: {len(pending)} unapplied migration(s): {revs}\n")
        sys.exit(1)
    print("\n  OK: schema is up to date ✓\n")


def _assert_db_reachable(db_url: str):
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        print(f"\n  Error: cannot connect to database — {exc}\n")
        sys.exit(1)


def _safe_url(url: str) -> str:
    """Mask password in URL for display."""
    try:
        from urllib.parse import urlparse, urlunparse
        p = urlparse(url)
        masked = p._replace(netloc=f"{p.username}:***@{p.hostname}" + (f":{p.port}" if p.port else ""))
        return urlunparse(masked)
    except Exception:
        return "(url parse error)"


def main():
    args = sys.argv[1:]

    if not args:
        cmd_status()
        return

    cmd = args[0].lower()

    if cmd == "upgrade":
        cmd_upgrade(args[1] if len(args) > 1 else "head")
    elif cmd == "downgrade":
        if len(args) < 2:
            print("  Error: provide a revision, e.g. python migrate.py downgrade -1\n")
            sys.exit(1)
        cmd_downgrade(args[1])
    elif cmd == "create":
        cmd_create(" ".join(args[1:]))
    elif cmd == "history":
        cmd_history()
    elif cmd == "check":
        cmd_check()
    elif cmd == "status":
        cmd_status()
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
