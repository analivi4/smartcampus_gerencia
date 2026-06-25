#!/bin/bash

# This script is the entry point for the Docker container. It runs the planner and captures its output.
VOLUME_PATH="/planner/runtime"
OUTPUT_PATH="$VOLUME_PATH/output"

# Create a directory to output files
mkdir -p "$OUTPUT_PATH"

echo "[INFO] Starting the planner..."

# Run the planner
popf3-clp "$@" > "$OUTPUT_PATH/plan.txt" 2> "$OUTPUT_PATH/error.log"

# Capture the exit code of the planner
EXIT_CODE=$?

# Show the plan if it was generated successfully, otherwise show the error log
if [ -s "$OUTPUT_PATH/plan.txt" ]; then
    cat "$OUTPUT_PATH/plan.txt"
else
    echo "[ERROR] Planner did not produce a plan. Check error.log for details."
    if [ -f "$OUTPUT_PATH/error.log" ]; then
        cat "$OUTPUT_PATH/error.log"
    fi
fi

exit $EXIT_CODE