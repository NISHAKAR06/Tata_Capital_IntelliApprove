from __future__ import annotations

from alembic import context
from sqlalchemy import engine_from_config, pool

# Alembic Config object provides access to values within the .ini file.
config = context.config

def run_migrations_offline():
    context.configure(url="sqlite:///./dev.db", literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
