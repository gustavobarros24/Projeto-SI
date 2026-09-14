#!/bin/bash

echo "Starting Python formatting with Black..."
black .

echo "Running Ruff linting and auto-fix..."
ruff check . --fix 

echo "Done! All Python files formatted and linted."
