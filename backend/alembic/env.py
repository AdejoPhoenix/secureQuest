from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from app.database import Base
from app.config import settings
import app.models  # noqa: F401 — register all models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _make_engine():
    """Build migration engine from app settings — same URL and SSL config as the app."""
    url = config.get_main_option("sqlalchemy.url") or settings.DATABASE_URL
    connect_args = {}
    # Render (and most managed Postgres) require SSL — honour the flag if present in the URL,
    # otherwise default to require when running against a non-localhost host.
    if "localhost" not in url and "127.0.0.1" not in url:
        connect_args["sslmode"] = "require"
    return create_engine(url, poolclass=pool.NullPool, connect_args=connect_args)


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url") or settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    engine = _make_engine()
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
