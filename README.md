# OPIO Prompts

Agent configuration files and setup utilities for agentic development systems.

## Installation

### Install UV

First, install UV (the Python package manager):

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Alternative (via pip):**
```bash
pip install uv
```

## Usage

### Setup Script

Use the setup script to create symlinks to AGENT.md for your agentic development system:

```bash
uv run scripts/setup.py [PROJECT_PATH] [OPTIONS]
```

### Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `PROJECT_PATH` | | Path to the target project directory (optional - will prompt if not provided) |
| `--system <NAME>` | `-s` | Agentic system(s) to use (can specify multiple) |
| `--uninstall` | `-u` | Remove existing symlinks |
| `--regenerate` | `-r` | Regenerate local template files |
| `--add-language` | `-l` | Add language-specific prompts to project |
| `--language <NAME>` | | Language to add (use with --add-language) |
| `--add-package` | `-p` | Add package prompts to project |
| `--package <NAME>` | | Package to add (use with --add-package) |
| `--remove-package` | | Remove package prompts from project |

### Basic Commands

#### Install Agent Systems

```bash
# Interactive mode - prompts for everything
uv run scripts/setup.py

# Single system
uv run scripts/setup.py /path/to/your/project --system "Amp"

# Multiple systems at once
uv run scripts/setup.py /path/to/your/project --system "Claude Code" --system "Cursor"

# Short flags
uv run scripts/setup.py ~/my-project -s "Claude Code" -s "Amp"
```

#### Add Language-Specific Prompts

```bash
# Interactive language selection
uv run scripts/setup.py ~/my-project --add-language

# Specify language directly
uv run scripts/setup.py ~/my-project --add-language --language python

# Short flag
uv run scripts/setup.py ~/my-project -l --language javascript
```

#### Add Package Prompts

```bash
# Interactive package selection
uv run scripts/setup.py ~/my-project --add-package

# Specify package directly
uv run scripts/setup.py ~/my-project --add-package --package fastapi

# Short flag
uv run scripts/setup.py ~/my-project -p --package fastapi

# Remove a package
uv run scripts/setup.py ~/my-project --remove-package --package fastapi
```

#### Maintenance Commands

```bash
# Regenerate local .mdc templates (after editing AGENT.md)
uv run scripts/setup.py --regenerate
uv run scripts/setup.py -r

# Remove all symlinks from a project
uv run scripts/setup.py ~/my-project --uninstall
uv run scripts/setup.py ~/my-project -u

# Remove specific system's symlink
uv run scripts/setup.py ~/my-project --uninstall --system "Cursor"
uv run scripts/setup.py ~/my-project -u -s "Cursor"
```

### Supported Systems

- **Claude Code** → Creates `CLAUDE.md` (symlink to `AGENT.md`)
- **Amp** → Creates `AGENT.md` (symlink to `AGENT.md`)
- **Cursor** → Creates `.cursor/rules/agent.mdc` (symlink to generated `.mdc` template)
- **Cline** → Creates `AGENT.md` (symlink to `AGENT.md`)

### Interactive Mode

When run without arguments, the script enters interactive mode:

```bash
uv run scripts/setup.py
```

This will:
1. Prompt for the target project directory path
2. Show a numbered list of available agentic systems
3. Allow you to select multiple systems (space-separated numbers, e.g., "1 3")
4. Create the appropriate symlinks

### Language Prompts

Add language-specific instructions to your project:

```bash
# Interactive - shows available languages and prompts for selection
uv run scripts/setup.py ~/my-project --add-language

# Direct - add Python prompts
uv run scripts/setup.py ~/my-project --add-language --language python
```

This creates:
- `prompts/` directory in your project
- Symlink to the language folder (e.g., `prompts/python/` → `lang/python/`)

### Package Prompts

Add framework or library-specific prompts to your project:

```bash
# Interactive - shows available packages and prompts for selection
uv run scripts/setup.py ~/my-project --add-package

# Direct - add FastAPI prompts
uv run scripts/setup.py ~/my-project --add-package --package fastapi

# Remove package prompts
uv run scripts/setup.py ~/my-project --remove-package --package fastapi
```

This:
- Creates `prompts/` directory in your project (if not exists)
- Symlinks the package folder (e.g., `prompts/fastapi/` → `packages/fastapi/`)
- Updates `project.md` with references to all package files (e.g., `@prompts/fastapi/core.md`)
- Is idempotent - running multiple times won't duplicate entries

### Examples

```bash
# Setup Claude Code and Cursor for a project
uv run scripts/setup.py ~/my-project -s "Claude Code" -s "Cursor"

# Add Python language prompts to existing project
uv run scripts/setup.py ~/my-project -l --language python

# Add FastAPI package prompts
uv run scripts/setup.py ~/my-project -p --package fastapi

# Interactive setup for new project
uv run scripts/setup.py
# Enter: ~/new-project
# Select: 1 3 (for Claude Code and Cursor)

# Update templates after editing AGENT.md
uv run scripts/setup.py --regenerate

# Clean up all symlinks before archiving project
uv run scripts/setup.py ~/old-project --uninstall
```

### How It Works

The script creates symlinks from your project directory to this repository's files:
- Direct symlinks for `.md` files (AGENT.md, CLAUDE.md)
- Generated templates for special formats (Cursor's `.mdc`)
- Language prompt directories linked to `lang/` folder
- Package prompt directories linked to `packages/` folder
- Automatic updates to `project.md` for package references

Updates to AGENT.md automatically propagate to all linked projects. For systems requiring special formats, use `--regenerate` to update local templates.
