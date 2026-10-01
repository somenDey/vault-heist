"""Alembic's entry point: connects to the database and runs migrations.

The database URL comes from the app's settings (DATABASE_URL), unless a caller
such as a test sets ``sqlalchemy.url`` explicitly.
"""

from logging.config import fileConfig

from alembic import context

from app.core.config import get_settings
from app.db.models import Base
from app.db.session import create_db_engine

config = context.config

# Use the logging settings in alembic.ini, so each migration is reported as it runs.
# disable_existing_loggers=False leaves the app's (and pytest's) loggers alone.
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

# The tables that `alembic revision --autogenerate` compares the database against.
target_metadata = Base.metadata


def database_url() -> str:
    """The URL to migrate: an explicit override, or the app's DATABASE_URL."""
    return config.get_main_option("sqlalchemy.url") or get_settings().database_url


def run_migrations_offline() -> None:
    """Write the migration SQL to stdout instead of running it (``--sql``)."""
    context.configure(
        url=database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Connect to the database and run the migrations."""
    engine = create_db_engine(database_url())
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # SQLite can't alter most columns in place. Batch mode rebuilds the
            # table instead, so future migrations work on SQLite and Postgres alike.
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
