#!/bin/sh
set -e

if ! python -c "from sqlalchemy import inspect; from db.database import engine; print(inspect(engine).has_table('newspaper'))" | grep True; then
  echo "Tables missing, running init_db.py..."
  python ./init_db.py
else
  echo "Tables exist, skipping init."
fi
echo "Starting app..."
exec python app/main.py