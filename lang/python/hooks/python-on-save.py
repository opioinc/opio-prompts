#!/usr/bin/env python3
# ABOUTME: Python hook for Claude Code that runs ruff format, check, and ty type checking on saved Python files
# ABOUTME: Logs all operations to hooks/logs with timestamps and structured output using loguru

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Any

from loguru import logger

# Set up logging to file in hooks/logs directory
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

# Configure loguru to log to file with rotation
log_file = log_dir / f"python-on-save-{datetime.now():%Y-%m-%d}.log"
logger.add(
    log_file,
    rotation="1 day",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
    level="DEBUG",
    enqueue=True,  # Thread-safe logging
)


def run_command(cmd: list[str], check: bool = False) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, and stderr."""
    logger.debug(f"Running command: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=check,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout, e.stderr
    except Exception as e:
        logger.error(f"Failed to run command {cmd}: {e}")
        return 1, "", str(e)


def process_file(file_path: str) -> dict[str, Any]:
    """Process a Python file with ruff and ty."""
    path = Path(file_path)

    # Check if it's a Python file
    if not path.suffix == ".py":
        logger.info(f"Skipping non-Python file: {file_path}")
        return {"target": file_path, "skipped": True, "reason": "not a Python file"}

    if not path.exists():
        logger.warning(f"File does not exist: {file_path}")
        return {"target": file_path, "skipped": True, "reason": "file does not exist"}

    logger.info(f"Processing Python file: {file_path}")
    results = {"target": file_path}

    # Run ruff format
    logger.debug("Running ruff format...")
    exit_code, stdout, stderr = run_command(["uv", "run", "ruff", "format", file_path])
    if exit_code != 0:
        logger.warning(f"Ruff format failed with exit code {exit_code}: {stderr}")
    else:
        logger.debug("Ruff format completed successfully")

    # Run ruff check with autofix and JSON output
    logger.debug("Running ruff check with autofix...")
    exit_code, stdout, stderr = run_command(
        ["uv", "run", "ruff", "check", "--fix", "--output-format", "json", file_path]
    )

    try:
        ruff_fix_results = json.loads(stdout) if stdout else []
    except json.JSONDecodeError:
        logger.error(f"Failed to parse ruff fix output: {stdout}")
        ruff_fix_results = []

    results["ruff_fix"] = ruff_fix_results
    logger.info(f"Ruff autofix found {len(ruff_fix_results)} issues")

    # Run ty type checking
    logger.debug("Running ty type checking...")
    exit_code, stdout, stderr = run_command(
        ["uv", "run", "ty", "check", "--output-format", "concise", file_path]
    )

    # Parse ty output to count errors
    error_count = stdout.count("error[") if stdout else 0

    ty_results = {
        "exit_code": exit_code,
        "error_count": error_count,
        "output": stdout.strip(),
    }
    results["ty"] = ty_results

    if exit_code == 0:
        logger.info("Type checking passed")
    else:
        logger.warning(f"Type checking found {error_count} errors")
        if stdout:
            for line in stdout.split("\n"):
                if "error[" in line:
                    logger.warning(f"  {line.strip()}")

    # Run final ruff check to see remaining issues
    logger.debug("Running final ruff check...")
    exit_code, stdout, stderr = run_command(
        ["uv", "run", "ruff", "check", "--output-format", "json", file_path]
    )

    try:
        ruff_final_results = json.loads(stdout) if stdout else []
    except json.JSONDecodeError:
        logger.error(f"Failed to parse ruff final output: {stdout}")
        ruff_final_results = []

    results["ruff_final"] = ruff_final_results

    if ruff_final_results:
        logger.warning(
            f"Final ruff check found {len(ruff_final_results)} remaining issues"
        )
        for issue in ruff_final_results[:5]:  # Log first 5 issues
            logger.warning(
                f"  {issue.get('filename', '')}:{issue.get('location', {}).get('row', '')} - {issue.get('message', '')}"
            )
    else:
        logger.info("Final ruff check passed")

    # Overall success determination
    success = ty_results["exit_code"] == 0 and len(ruff_final_results) == 0
    results["success"] = success

    if success:
        logger.success(f"✅ All checks passed for {file_path}")
    else:
        logger.warning(f"⚠️ Issues remain in {file_path}")

    return results


def main():
    """Main entry point for the hook."""
    logger.info("=" * 60)
    logger.info("Python-on-save hook started")

    # Check if we have command line arguments (CLI mode)
    if len(sys.argv) > 1:
        # CLI mode - process command line arguments
        logger.info("Running in CLI mode")
        targets = sys.argv[1:]

        for target in targets:
            results = process_file(target)
            print(json.dumps(results, indent=2))
    elif sys.stdin.isatty():
        # Interactive mode with no arguments - process current directory
        logger.info("Running in CLI mode (no args, processing current directory)")
        results = process_file(".")
        print(json.dumps(results, indent=2))
    else:
        # Hook mode - read JSON from stdin
        logger.info("Running in hook mode (Claude Code PostToolUse)")
        try:
            input_data = sys.stdin.read()
            logger.debug(
                f"Received input: {input_data[:500]}..."
            )  # Log first 500 chars

            if not input_data:
                logger.warning("No input received from stdin")
                print(json.dumps({"error": "No input received"}))
                return

            data = json.loads(input_data)
            logger.debug(f"Parsed JSON with tool: {data.get('tool_name', 'unknown')}")

            tool_name = data.get("tool_name", "")

            # Only process Write, Edit, and MultiEdit tools
            if tool_name in ["Write", "Edit", "MultiEdit"]:
                # Extract file path from tool_input
                tool_input = data.get("tool_input", {})
                file_path = tool_input.get("file_path", "")

                if file_path:
                    logger.info(f"Processing {tool_name} operation on {file_path}")
                    results = process_file(file_path)
                else:
                    logger.warning(f"No file_path found in {tool_name} input")
                    results = {"error": "No file_path found in tool input"}
            else:
                logger.debug(f"Ignoring tool: {tool_name}")
                results = {
                    "tool": tool_name,
                    "skipped": True,
                    "reason": "not a file editing tool",
                }

            # Output results as JSON for Claude Code
            # Check if we should block due to errors
            if not results.get("success", True) and not results.get("skipped", False):
                # Build error message for Claude
                error_messages = []

                # Add type checking errors
                ty_results = results.get("ty", {})
                if ty_results.get("exit_code", 0) != 0:
                    error_messages.append(
                        f"Type checking found {ty_results.get('error_count', 0)} errors:"
                    )
                    if ty_results.get("output"):
                        error_messages.append(ty_results["output"])

                # Add ruff errors
                ruff_final = results.get("ruff_final", [])
                if ruff_final:
                    error_messages.append(
                        f"\nRuff found {len(ruff_final)} linting issues:"
                    )
                    for issue in ruff_final[:10]:  # Show first 10 issues
                        location = issue.get("location", {})
                        error_messages.append(
                            f"  {issue.get('filename', '')}:{location.get('row', '')}:{location.get('column', '')} "
                            f"{issue.get('code', '')} {issue.get('message', '')}"
                        )

                # Block with reason
                blocking_response = {
                    "decision": "block",
                    "reason": (
                        "The file has errors that must be fixed before continuing.\n"
                        "Please fix ALL the following issues (even if they existed before your changes):\n\n"
                        + "\n".join(error_messages)
                        + "\n\nFix these issues and try again."
                    ),
                }
                print(json.dumps(blocking_response, indent=2))

                # Also write to stderr for visibility
                print("\n".join(error_messages), file=sys.stderr)

                # Exit with code 2 to ensure Claude sees the errors
                sys.exit(2)
            else:
                # Success or skipped - output normally
                print(json.dumps(results, indent=2))

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON input: {e}")
            print(json.dumps({"error": f"Invalid JSON: {e}"}))
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            print(json.dumps({"error": str(e)}))

    logger.info("Python-on-save hook completed")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
