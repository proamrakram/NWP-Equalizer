import os
print(__file__)

MIGRATION_DIR = os.path.join(
        os.path.dirname(__file__), "model", "migrations"
    )
print(MIGRATION_DIR)
