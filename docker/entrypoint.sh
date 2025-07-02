#!/bin/sh
set -e

if [ -f .env ]; then
  echo "Loading environment variables from .env"
  export $(grep -v '^#' .env | xargs)
fi


if ! python -c "from sqlalchemy import inspect; from db.database import engine; print(inspect(engine).has_table('newspaper'))" | grep True; then
  echo "Tables missing, running init_db.py..."
  python ./init_db.py
else
  echo "Tables exist, skipping init."
fi
echo "Starting app..."
python ./main.py
