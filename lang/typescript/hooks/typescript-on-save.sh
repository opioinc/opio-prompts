#!/bin/bash
# ABOUTME: Wrapper script that calls the TypeScript implementation of the hook
# ABOUTME: This allows the hook to be executed as a shell command while using TypeScript for logic

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Execute the TypeScript file with tsx (TypeScript execute)
# If tsx is not available, fall back to ts-node, then to compiling and running with node
if command -v tsx &> /dev/null; then
    # tsx is the fastest TypeScript executor
    exec tsx "$SCRIPT_DIR/typescript-on-save.ts" "$@"
elif command -v ts-node &> /dev/null; then
    # ts-node is a common alternative
    exec ts-node "$SCRIPT_DIR/typescript-on-save.ts" "$@"
else
    # Fallback: compile and run with node
    # First check if we have a compiled version
    if [ ! -f "$SCRIPT_DIR/typescript-on-save.js" ] || [ "$SCRIPT_DIR/typescript-on-save.ts" -nt "$SCRIPT_DIR/typescript-on-save.js" ]; then
        # Compile the TypeScript file
        if command -v tsc &> /dev/null; then
            tsc --target es2020 --module commonjs --outDir "$SCRIPT_DIR" "$SCRIPT_DIR/typescript-on-save.ts"
        else
            echo "Error: No TypeScript executor found (tsx, ts-node, or tsc)" >&2
            echo "Please install one of them with: npm install -g tsx" >&2
            exit 1
        fi
    fi
    
    # Run the compiled JavaScript
    exec node "$SCRIPT_DIR/typescript-on-save.js" "$@"
fi