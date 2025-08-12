# Hook Installation System

## Overview
The language setup system now automatically installs hooks for AI agents when setting up language-specific prompts. This ensures that code quality checks run automatically when files are edited.

## Directory Structure

### Source Structure (in this repo)
```
lang/
├── python/
│   ├── hooks/
│   │   ├── claude.json         # Claude agent configuration
│   │   └── python-on-save.py   # Hook script
│   └── *.md                     # Language prompts
└── typescript/
    ├── hooks/
    │   ├── claude.json          # Claude agent configuration
    │   ├── typescript-on-save.sh
    │   ├── typescript-on-save.ts
    │   └── typescript-on-save.js
    └── *.md                     # Language prompts
```

### Target Project Structure (after installation)
```
your_project/
├── hooks/
│   ├── claude/              # Claude-specific hooks
│   │   ├── python-on-save.py
│   │   └── typescript-on-save.sh (+ .ts, .js)
│   ├── cursor/              # Future: Cursor-specific hooks
│   └── windsurf/            # Future: Windsurf-specific hooks
├── .claude/
│   └── settings.json        # Claude configuration with hooks
├── prompts/
│   ├── python/              # Symlink to lang/python
│   └── typescript/          # Symlink to lang/typescript
└── project.md               # References to prompt files
```

## Hook Configuration Format

Each language has agent-specific configuration files (`claude.json`, `cursor.json`, etc.):

```json
{
  "agent": "claude",
  "language": "python",
  "dependencies": {
    "commands": ["uv"],              // Required commands
    "optional_commands": ["tsx"],    // At least one must exist
    "python_packages": ["loguru"]    // Information only
  },
  "files": ["python-on-save.py"],    // Files to copy
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "uv run hooks/claude/python-on-save.py",
            "blocking": true,
            "blocking_failure_message": "❌ Python linting/type checking failed!"
          }
        ]
      }
    ]
  }
}
```

## Installation Process

When you run `setup_language_prompts()`:

1. **Dependency Check**: Verifies required tools are installed
2. **File Copy**: Copies hook scripts to `hooks/{agent}/`
3. **Settings Update**: Updates `.claude/settings.json` additively
4. **Permissions**: Makes scripts executable

## Key Features

### Automatic Installation
- Hooks are installed automatically when setting up a language
- Dependencies are checked before installation
- Existing hooks are preserved (additive merge)

### Agent-Specific
- Different agents (Claude, Cursor, Windsurf) have separate configurations
- Hook scripts are stored in agent-specific directories
- Settings are managed per-agent

### Clean Uninstall
- `uninstall_language_prompts()` removes both prompts and hooks
- Settings are cleaned up properly
- Empty directories are removed

## Usage Examples

### Install Python with hooks
```python
from scripts.language import setup_language_prompts
setup_language_prompts(Path("."), "python", agent="claude")
```

### Uninstall Python and its hooks
```python
from scripts.language import uninstall_language_prompts
uninstall_language_prompts(Path("."), "python", agent="claude")
```

### Check dependencies
```python
from scripts.language import check_hook_dependencies
deps_ok, missing = check_hook_dependencies("python", "claude")
if not deps_ok:
    print(f"Missing: {missing}")
```

## Adding New Language Hooks

1. Create hook script in `lang/{language}/hooks/`
2. Create `claude.json` configuration file
3. Specify dependencies, files, and hook configuration
4. Test with `scripts/test_hooks.py`

## Dependencies

### Python Hooks
- `uv`: Python package manager
- `loguru`: Logging library (installed in project)

### TypeScript Hooks
- `node`: JavaScript runtime
- One of: `tsx`, `ts-node`, or `tsc`

## Testing

Run the test script to verify hook installation:
```bash
uv run scripts/test_hooks.py
```

This will:
- Check dependencies
- Install hooks to a temp directory
- Verify files and settings
- Test uninstall process
- Show final directory structure