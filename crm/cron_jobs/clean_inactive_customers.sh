#!/bin/bash

# Get the current working directory (cwd) before any changes
ORIGINAL_CWD=$(pwd)
echo "Original working directory: $ORIGINAL_CWD"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Changing to project root: $PROJECT_ROOT"
# Change to the project root directory
cd "$PROJECT_ROOT" || {
    echo "Failed to change to project root directory"
    exit 1
}

# Print current working directory for debugging
echo "Current working directory: $(pwd)"

# Activate virtual environment if exists
if [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment from venv/bin/activate"
    source venv/bin/activate
elif [ -f "../venv/bin/activate" ]; then
    echo "Activating virtual environment from ../venv/bin/activate"
    source ../venv/bin/activate
else
    echo "No virtual environment found, proceeding without activation"
fi

# Execute the Django management command
echo "Running Django management command..."
python manage.py clean_inactive_customers

# Store the exit status
status=$?

# Change back to the original directory
echo "Returning to original directory: $ORIGINAL_CWD"
cd "$ORIGINAL_CWD" || {
    echo "Warning: Failed to return to original directory"
    exit 1
}

exit $status