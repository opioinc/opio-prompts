# OPIO Prompts

Agent configuration files and setup utilities for agentic development systems.

## Quick Navigation

- [Installation](#installation) - Get started with UV package manager
- [Feature Support Matrix](#feature-support-matrix) - See what's supported for each AI agent
- [Command Line Options](#command-line-options) - All available CLI flags
- [Language Prompts](#language-prompts) - Add language-specific instructions
- [Hooks](#hooks-code-quality-automation) - Automatic code quality checks
- [Slash Commands](#slash-commands) - Auto-installed Claude Code commands
- [Package Prompts](#package-prompts) - Framework/library specific prompts
- [Examples](#examples) - Common usage patterns

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
| `--add-language` | `-l` | Add language-specific prompts to project (includes hooks by default) |
| `--language <NAME>` | | Language to add (use with --add-language) |
| `--no-hooks` | | Skip hook installation when adding languages |
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
- **Codex** → Creates `AGENTS.md` (symlink to `AGENT.md`)

## Feature Support Matrix

This table shows which features are currently supported for each AI agent system:

| Feature | Claude Code | Cursor | Amp | Cline | Codex | Notes |
|---------|:-----------:|:------:|:---:|:-----:|:-----:|-------|
| **Core Prompts** |
| AGENT.md symlink | ✅ | ✅ | ✅ | ✅ | ✅ | Base agent configuration |
| Custom file path | ✅ | ✅ | ❌ | ❌ | ✅ | Claude: CLAUDE.md, Cursor: .cursor/rules/agent.mdc, Codex: AGENTS.md |
| Auto-propagate updates | ✅ | ⚠️ | ✅ | ✅ | ✅ | Cursor requires `--regenerate` for .mdc format |
| **Language Support** |
| Language prompts | ✅ | ✅ | ✅ | ✅ | ✅ | All agents can use language prompts |
| Python prompts | ✅ | ✅ | ✅ | ✅ | ✅ | Via @prompts/python/ references |
| TypeScript prompts | ✅ | ✅ | ✅ | ✅ | ✅ | Via @prompts/typescript/ references |
| Rust prompts | ✅ | ✅ | ✅ | ✅ | ✅ | Via @prompts/rust/ references |
| **Slash Commands** |
| Command support | ✅ | ❌ | ❌ | ❌ | ❌ | Claude Code only |
| /read_project_files | ✅ | ❌ | ❌ | ❌ | ❌ | Auto-installed with Claude Code |
| **Hooks (Auto Quality Checks)** |
| Hook support | ✅ | 🚧 | 🚧 | 🚧 | 🚧 | Currently Claude Code only, Codex has notify config |
| Python hooks | ✅ | ❌ | ❌ | ❌ | ❌ | Ruff + Ty type checking |
| TypeScript hooks | ✅ | ❌ | ❌ | ❌ | ❌ | TSX/TS-Node linting |
| Auto-install hooks | ✅ | ❌ | ❌ | ❌ | ❌ | With --add-language |
| Settings integration | ✅ | ❌ | ❌ | ❌ | ⚠️ | .claude/settings.json, Codex uses config.toml |
| **Package Support** |
| Package prompts | ✅ | ✅ | ✅ | ✅ | ✅ | Framework/library specific prompts |
| FastAPI prompts | ✅ | ✅ | ✅ | ✅ | ✅ | Via @prompts/fastapi/ |
| Svelte prompts | ✅ | ✅ | ✅ | ✅ | ✅ | Via @prompts/svelte/ |
| project.md updates | ✅ | ✅ | ✅ | ✅ | ✅ | Auto-adds package references |
| **Management** |
| Interactive setup | ✅ | ✅ | ✅ | ✅ | ✅ | Via setup.py script |
| Multi-agent install | ✅ | ✅ | ✅ | ✅ | ✅ | Can install multiple agents at once |
| Uninstall support | ✅ | ✅ | ✅ | ✅ | ✅ | Clean removal of symlinks |
| Selective uninstall | ✅ | ✅ | ✅ | ✅ | ✅ | Remove specific languages/packages |

### Legend

- ✅ **Fully Supported** - Feature is implemented and working
- ⚠️ **Partial Support** - Feature works with limitations
- 🚧 **Planned** - On the roadmap for future implementation
- ❌ **Not Supported** - Not available for this agent
- N/A **Not Applicable** - Feature doesn't apply to this agent

### Notes on Slash Commands

Slash commands are automatically installed when you set up **Claude Code**. These provide quick shortcuts for common tasks:

- `/read_project_files` - Reads project.md and all referenced files to establish project context and rules

Commands are installed as symlinks to `.claude/commands/` in your project directory. Updates to the command definitions in this repo will automatically propagate to all linked projects.

### Notes on Hook Support

Currently, hooks are only implemented for **Claude Code**. The architecture supports adding hooks for other agents:
- **Cursor**: Would use `.cursor/hooks/` directory and cursor-specific settings
- **Amp**: Would require understanding Amp's extension/hook system
- **Cline**: Would need integration with Cline's workflow system
- **Codex**: Has built-in notify configuration for event notifications but doesn't support file-save hooks yet

To request hook support for additional agents, please open an issue on GitHub.

### Available Languages & Packages

#### Currently Available Languages
- **Python** - Full support with hooks (ruff, ty)
- **TypeScript** - Full support with hooks (tsx/ts-node)
- **Rust** - Prompts only (no hooks yet)

#### Currently Available Packages
- **FastAPI** - Python web framework prompts
- **Svelte** - Frontend framework prompts

To see the latest list of available languages and packages, run:
```bash
# List available languages
ls lang/

# List available packages
ls packages/
```

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

# Add language without hooks
uv run scripts/setup.py ~/my-project --add-language --language python --no-hooks
```

This creates:
- `prompts/` directory in your project
- Symlink to the language folder (e.g., `prompts/python/` → `lang/python/`)
- **Automatic hook installation** (see Hooks section below)

### Hooks (Code Quality Automation)

When you add a language to your project, **hooks are automatically installed by default** to ensure code quality. These hooks run when you edit files in supported AI agents (like Claude Code).

#### What Hooks Do

Hooks automatically run code quality checks when you save or edit files:
- **Python**: Runs `ruff` for formatting/linting and `ty` for type checking
- **TypeScript**: Runs linting and type checking via `tsx`/`ts-node`

#### How Hooks Get Installed

When you run `--add-language`:
1. Hook scripts are copied to `hooks/claude/` in your project
2. Claude Code settings are updated in `.claude/settings.json`
3. Dependencies are verified (e.g., `uv` for Python, `node` for TypeScript)

#### Controlling Hook Installation

```bash
# Install language WITH hooks (default)
uv run scripts/setup.py ~/my-project --add-language --language python

# Install language WITHOUT hooks
uv run scripts/setup.py ~/my-project --add-language --language python --no-hooks

# Remove language and its hooks
uv run scripts/setup.py ~/my-project --remove-language --language python
```

#### Project Structure After Hook Installation

```
your_project/
├── hooks/
│   └── claude/              # Claude-specific hooks
│       ├── python-on-save.py
│       └── typescript-on-save.sh
├── .claude/
│   └── settings.json        # Hook configuration
└── prompts/                 # Language prompts
```

#### Dependencies Required

**Python hooks:**
- `uv` (Python package manager)
- `loguru` (installed automatically in project)

**TypeScript hooks:**
- `node`
- One of: `tsx`, `ts-node`, or `tsc`

If dependencies are missing, the installation will fail with a clear error message.

### Slash Commands

When you install Claude Code, slash commands are automatically installed to `.claude/commands/` in your project. These commands provide quick shortcuts for common workflows.

#### Available Commands

| Command | Description |
|---------|-------------|
| `/read_project_files` | Reads project.md and all referenced files to establish project context |

#### How Commands Work

Commands are installed as symlinks, so updates to this repo automatically propagate to your project. The commands are stored in your project's `.claude/commands/` directory.

#### Project Structure After Command Installation

```
your_project/
├── .claude/
│   ├── commands/
│   │   └── read_project_files.md  # Symlink to repo command
│   └── settings.json              # Hook configuration (if hooks installed)
└── ...
```

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

# Add Python language prompts to existing project (with hooks)
uv run scripts/setup.py ~/my-project -l --language python

# Add Python language prompts WITHOUT hooks
uv run scripts/setup.py ~/my-project -l --language python --no-hooks

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
