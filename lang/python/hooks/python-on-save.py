#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "loguru",
#     "ruff",
#     "ty",
# ]
# ///
# ABOUTME: Python hook for Claude Code that runs ruff format, check, and type checking on saved Python files
# ABOUTME: Supports both UV and Poetry projects with automatic detection and appropriate tool execution

import json
import os
import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
from typing import Any

from loguru import logger

# Set up logging to file in hooks/logs directory
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

# Configure loguru to log to file with rotation
log_file = log_dir / f"python-on-save-{datetime.now():%Y-%m-%d}.log"
# Remove default handlers to avoid duplicate logs
try:
    logger.remove()
except Exception:
    pass
logger.add(
    log_file,
    rotation="1 day",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
    level="DEBUG",
    enqueue=True,  # Thread-safe logging
)
# Optional: console sink for interactive runs
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | {level: <8} | {message}", level="INFO")


class PackageManager(ABC):
    """Abstract base class for package manager operations."""

    @abstractmethod
    def get_run_prefix(self) -> list[str]:
        """Return command prefix for running tools."""
        pass

    @abstractmethod
    def has_type_checker(self) -> bool:
        """Check if type checker is available."""
        pass

    @abstractmethod
    def get_type_check_command(self, file_path: str) -> list[str]:
        """Return type checking command."""
        pass

    @abstractmethod
    def parse_type_check_output(self, stdout: str, stderr: str, exit_code: int) -> dict[str, Any]:
        """Parse type checker output into standardized format."""
        pass


class UVManager(PackageManager):
    """Package manager for UV projects."""

    def get_run_prefix(self) -> list[str]:
        return ["uv", "run"]

    def has_type_checker(self) -> bool:
        # Check if ty is available in uv environment
        return check_command_exists(["uv", "run", "ty", "--version"])

    def get_type_check_command(self, file_path: str) -> list[str]:
        return ["uv", "run", "ty", "check", "--output-format", "concise", file_path]

    def parse_type_check_output(self, stdout: str, stderr: str, exit_code: int) -> dict[str, Any]:
        # Parse ty output to count errors
        error_count = stdout.count("error[") if stdout else 0
        return {
            "exit_code": exit_code,
            "error_count": error_count,
            "output": stdout.strip(),
        }


class PoetryManager(PackageManager):
    """Package manager for Poetry projects."""

    def get_run_prefix(self) -> list[str]:
        return ["poetry", "run"]

    def has_type_checker(self) -> bool:
        # Check for ty first (newest/preferred)
        if check_command_exists(["poetry", "run", "ty", "--version"]):
            return True
        # Check for mypy
        if check_command_exists(["poetry", "run", "mypy", "--version"]):
            return True
        # Check for pyright
        if check_command_exists(["poetry", "run", "pyright", "--version"]):
            return True
        return False

    def get_type_check_command(self, file_path: str) -> list[str]:
        # Prefer ty if available
        if check_command_exists(["poetry", "run", "ty", "--version"]):
            return ["poetry", "run", "ty", "check", "--output-format", "concise", file_path]
        # Fall back to mypy
        if check_command_exists(["poetry", "run", "mypy", "--version"]):
            return ["poetry", "run", "mypy", "--no-error-summary", "--no-color-output", file_path]
        # Fall back to pyright
        if check_command_exists(["poetry", "run", "pyright", "--version"]):
            return ["poetry", "run", "pyright", file_path]
        return []

    def parse_type_check_output(self, stdout: str, stderr: str, exit_code: int) -> dict[str, Any]:
        # Parse ty/mypy/pyright output
        error_count = 0

        # For ty, count lines with "error["
        if "error[" in stdout:
            error_count = stdout.count("error[")
        # For mypy, count lines with ": error:"
        elif ": error:" in stdout:
            error_count = stdout.count(": error:")
        # For pyright, look for "X errors" in output
        elif "error" in stdout.lower():
            import re

            match = re.search(r"(\d+)\s+error", stdout)
            if match:
                error_count = int(match.group(1))

        return {
            "exit_code": exit_code,
            "error_count": error_count,
            "output": stdout.strip(),
        }


class DirectManager(PackageManager):
    """Direct execution without package manager."""

    def get_run_prefix(self) -> list[str]:
        return []

    def has_type_checker(self) -> bool:
        # Check if mypy is directly available
        return check_command_exists(["mypy", "--version"])

    def get_type_check_command(self, file_path: str) -> list[str]:
        if check_command_exists(["mypy", "--version"]):
            return ["mypy", "--no-error-summary", "--no-color-output", file_path]
        return []

    def parse_type_check_output(self, stdout: str, stderr: str, exit_code: int) -> dict[str, Any]:
        # Parse mypy output
        error_count = stdout.count(": error:") if stdout else 0
        return {
            "exit_code": exit_code,
            "error_count": error_count,
            "output": stdout.strip(),
        }


def check_command_exists(cmd: list[str]) -> bool:
    """Check if a command exists and is executable."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return False


def detect_package_manager() -> PackageManager:
    """Detect which package manager is being used in the current project."""
    # Allow override via environment variable
    pm_override = os.environ.get("PYTHON_HOOK_PACKAGE_MANAGER", "").lower()
    if pm_override == "uv":
        logger.info("Using UV package manager (from environment)")
        return UVManager()
    elif pm_override == "poetry":
        logger.info("Using Poetry package manager (from environment)")
        return PoetryManager()
    elif pm_override == "direct":
        logger.info("Using direct execution (from environment)")
        return DirectManager()

    # Auto-detect based on files
    cwd = Path.cwd()

    # Priority 1: Check for Poetry (poetry.lock is most definitive)
    if (cwd / "poetry.lock").exists():
        logger.info("Detected Poetry project (poetry.lock found)")
        return PoetryManager()

    # Priority 2: Check for UV (uv.lock is most definitive)
    if (cwd / "uv.lock").exists():
        logger.info("Detected UV project (uv.lock found)")
        return UVManager()

    # Priority 3: Check pyproject.toml for tool configuration
    pyproject_path = cwd / "pyproject.toml"
    if pyproject_path.exists():
        try:
            with open(pyproject_path) as f:
                content = f.read()
                # Check for Poetry first (more specific)
                if "[tool.poetry]" in content:
                    logger.info("Detected Poetry project (pyproject.toml has [tool.poetry])")
                    return PoetryManager()
                # Then check for UV-style project
                elif "[project]" in content:
                    # Additional check: if poetry.lock doesn't exist but [project] exists,
                    # it could still be a Poetry project without lock file
                    # Check for specific UV indicators
                    if "[tool.uv]" in content or "uv.workspace" in content:
                        logger.info("Detected UV project (pyproject.toml has UV configuration)")
                        return UVManager()
                    # If [project] exists without UV indicators, check if Poetry is installed
                    elif check_command_exists(["poetry", "--version"]):
                        # Try to detect if this is managed by Poetry
                        try:
                            # Run poetry check to see if it recognizes the project
                            result = subprocess.run(
                                ["poetry", "check"],
                                capture_output=True,
                                timeout=5,
                                cwd=cwd,
                            )
                            if result.returncode == 0:
                                logger.info("Detected Poetry project (poetry check succeeded)")
                                return PoetryManager()
                        except (subprocess.SubprocessError, FileNotFoundError, OSError):
                            pass
                    # Default to UV for [project] without other indicators
                    logger.info("Detected UV project (pyproject.toml has [project])")
                    return UVManager()
        except Exception as e:
            logger.warning(f"Error reading pyproject.toml: {e}")

    # Priority 4: Try to detect based on available commands
    # Check Poetry first since it's more established
    if check_command_exists(["poetry", "--version"]):
        # Additional check: see if we're in a Poetry virtual environment
        if os.environ.get("POETRY_ACTIVE") == "1" or "poetry" in os.environ.get("VIRTUAL_ENV", ""):
            logger.info("Detected active Poetry environment")
            return PoetryManager()
        logger.info("Detected Poetry installation, using Poetry")
        return PoetryManager()

    if check_command_exists(["uv", "--version"]):
        logger.info("Detected UV installation, using UV")
        return UVManager()

    # Default to direct execution
    logger.warning("No package manager detected, using direct execution")
    return DirectManager()


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


def process_file(file_path: str, pm: PackageManager) -> dict[str, Any]:
    """Process a Python file with ruff and type checking using the appropriate package manager."""
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

    # Get command prefix
    run_prefix = pm.get_run_prefix()

    # Run ruff format
    logger.debug("Running ruff format...")
    cmd = run_prefix + ["ruff", "format", file_path]
    exit_code, stdout, stderr = run_command(cmd)
    if exit_code != 0:
        logger.warning(f"Ruff format failed with exit code {exit_code}: {stderr}")
    else:
        logger.debug("Ruff format completed successfully")

    # Run ruff check with autofix and JSON output
    logger.debug("Running ruff check with autofix...")
    cmd = run_prefix + ["ruff", "check", "--fix", "--output-format", "json", file_path]
    exit_code, stdout, stderr = run_command(cmd)

    try:
        ruff_fix_results = json.loads(stdout) if stdout else []
    except json.JSONDecodeError:
        logger.error(f"Failed to parse ruff fix output: {stdout}")
        ruff_fix_results = []

    results["ruff_fix"] = ruff_fix_results
    logger.info(f"Ruff autofix found {len(ruff_fix_results)} issues")

    # Run type checking (if available)
    if pm.has_type_checker():
        logger.debug("Running type checking...")
        type_check_cmd = pm.get_type_check_command(file_path)
        if type_check_cmd:
            exit_code, stdout, stderr = run_command(type_check_cmd)
            ty_results = pm.parse_type_check_output(stdout, stderr, exit_code)
        else:
            logger.warning("Type checker command not available")
            ty_results = {"exit_code": 0, "error_count": 0, "output": ""}
    else:
        logger.info("No type checker available, skipping type checking")
        ty_results = {"exit_code": 0, "error_count": 0, "output": "", "skipped": True}

    results["ty"] = ty_results

    if ty_results.get("skipped"):
        logger.info("Type checking skipped")
    elif ty_results["exit_code"] == 0:
        logger.info("Type checking passed")
    else:
        logger.warning(f"Type checking found {ty_results['error_count']} errors")
        if ty_results["output"]:
            for line in ty_results["output"].split("\n")[:10]:  # Show first 10 lines
                if line.strip():
                    logger.warning(f"  {line.strip()}")

    # Run final ruff check to see remaining issues
    logger.debug("Running final ruff check...")
    cmd = run_prefix + ["ruff", "check", "--output-format", "json", file_path]
    exit_code, stdout, stderr = run_command(cmd)

    try:
        ruff_final_results = json.loads(stdout) if stdout else []
    except json.JSONDecodeError:
        logger.error(f"Failed to parse ruff final output: {stdout}")
        ruff_final_results = []

    results["ruff_final"] = ruff_final_results

    if ruff_final_results:
        logger.warning(f"Final ruff check found {len(ruff_final_results)} remaining issues")
        for issue in ruff_final_results[:5]:  # Log first 5 issues
            logger.warning(
                f"  {issue.get('filename', '')}:{issue.get('location', {}).get('row', '')} - {issue.get('message', '')}"
            )
    else:
        logger.info("Final ruff check passed")

    # Overall success determination
    # Consider type checking optional if it's skipped
    type_check_success = ty_results.get("skipped", False) or ty_results["exit_code"] == 0
    success = type_check_success and len(ruff_final_results) == 0
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

    # Detect package manager once
    pm = detect_package_manager()

    # Check if we have command line arguments (CLI mode)
    if len(sys.argv) > 1:
        # CLI mode - process command line arguments
        logger.info("Running in CLI mode")
        targets = sys.argv[1:]

        for target in targets:
            results = process_file(target, pm)
            print(json.dumps(results, indent=2))
    elif sys.stdin.isatty():
        # Interactive mode with no arguments - process current directory
        logger.info("Running in CLI mode (no args, processing current directory)")
        results = process_file(".", pm)
        print(json.dumps(results, indent=2))
    else:
        # Hook mode - read JSON from stdin
        logger.info("Running in hook mode (Claude Code PostToolUse)")
        try:
            input_data = sys.stdin.read()
            logger.debug(f"Received input: {input_data[:500]}...")  # Log first 500 chars

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
                    results = process_file(file_path, pm)
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

                # Add type checking errors (only if not skipped)
                ty_results = results.get("ty", {})
                if not ty_results.get("skipped", False) and ty_results.get("exit_code", 0) != 0:
                    error_messages.append(f"Type checking found {ty_results.get('error_count', 0)} errors:")
                    if ty_results.get("output"):
                        error_messages.append(ty_results["output"])

                # Add ruff errors
                ruff_final = results.get("ruff_final", [])
                if ruff_final:
                    error_messages.append(f"\nRuff found {len(ruff_final)} linting issues:")
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
