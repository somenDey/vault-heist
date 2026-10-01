"""The migrations must build exactly the tables the models describe."""

from pathlib import Path

from alembic import command
from alembic.config import Config

BACKEND_DIR = Path(__file__).resolve().parents[2]


def alembic_config(database_path: Path) -> Config:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path.as_posix()}")
    return config


def test_migrations_match_the_models(tmp_path: Path) -> None:
    config = alembic_config(tmp_path / "migrated.db")

    command.upgrade(config, "head")

    # Fails if the models have changed without a new migration.
    command.check(config)


def test_migrations_can_be_undone(tmp_path: Path) -> None:
    config = alembic_config(tmp_path / "migrated.db")

    command.upgrade(config, "head")
    command.downgrade(config, "base")
    command.upgrade(config, "head")
