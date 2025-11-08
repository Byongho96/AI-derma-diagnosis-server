#!/bin/bash

echo "Running database pre-start script..."
python -m app.initial_data
echo "Pre-start script finished."

exec "$@"s