from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, text
from alembic import context
from app.models import Base
import time
import sys

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

def run_migrations_online():
    connectable = None
    for _ in range(30):  # ждём до 30 секунд
        try:
            connectable = engine_from_config(
                config.get_section(config.config_ini_section),
                prefix="sqlalchemy.",
                poolclass=pool.NullPool,
            )
            with connectable.connect() as connection:
                connection.execute(text("SELECT 1"))
            break
        except Exception as e:
            print(f"Waiting for DB... {e}")
            time.sleep(2)
    else:
        print("Could not connect to database", file=sys.stderr)
        sys.exit(1)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()