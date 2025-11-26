# ABOUTME: Core functionality for agent setup and template generation
# ABOUTME: Handles symlink creation, template generation, and system management

from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from rich import print as rprint
from rich.prompt import Confirm

# Map of agentic systems to their expected file names and source files
AGENTIC_SYSTEMS = {
    "Claude Code": {"path": "CLAUDE.md", "source": "AGENT.md"},
    "Amp": {"path": "AGENT.md", "source": "AGENT.md"},
    "Cursor": {
        "path": ".cursor/rules/agent.mdc",
        "source": "generated/cursor-agent.mdc",
    },
    "Cline": {"path": "AGENT.md", "source": "AGENT.md"},
    "Codex": {"path": "AGENTS.md", "source": "AGENT.md"},
}


def get_repo_root() -> Path:
    """Get the path to the repository root"""
    script_dir = Path(__file__).parent
    return script_dir.parent


def get_source_agent_md() -> Path:
    """Get the path to the source AGENT.md file"""
    return get_repo_root() / "AGENT.md"


def generate_local_templates() -> None:
    """Generate local template files for non-markdown systems"""
    repo_root = get_repo_root()
    generated_dir = repo_root / "generated"
    generated_dir.mkdir(exist_ok=True)

    # Generate cursor-agent.mdc
    source_agent_md = get_source_agent_md()
    if not source_agent_md.exists():
        rprint(f"[red]Error: Source AGENT.md not found at {source_agent_md}[/red]")
        return

    agent_content = source_agent_md.read_text()

    # Get current timestamp
    now = datetime.utcnow()
    timestamp = int(now.timestamp())
    human_date = now.strftime("%Y-%m-%d %H:%M:%S UTC")

    mdc_content = f"""---
description: Agent development guidelines and best practices
globs: "**/*"
alwaysApply: true
---

<rule>
  <meta>
    <title>Agent Development Guidelines</title>
    <description>Core development guidelines and best practices for AI-assisted development</description>
    <created-at utc-timestamp="{timestamp}">{human_date}</created-at>
    <last-updated-at utc-timestamp="{timestamp}">{human_date}</last-updated-at>
    <applies-to>
      <file-matcher glob="**/*">All project files</file-matcher>
    </applies-to>
  </meta>
  <requirements>
    <requirement priority="critical">
      <description>Follow agent development guidelines as specified in AGENT.md</description>
      <examples>
        <example title="Development Guidelines">
          <correct-example title="Agent Guidelines" conditions="When working on any project files" expected-result="Code follows established patterns" correctness-criteria="Adheres to team conventions and AI collaboration patterns"><![CDATA[
{agent_content}
          ]]></correct-example>
        </example>
      </examples>
    </requirement>
  </requirements>
  <references>
    <reference as="context" href="../AGENT.md" reason="Source of truth for agent development guidelines">AGENT.md</reference>
  </references>
</rule>
"""

    cursor_template = generated_dir / "cursor-agent.mdc"
    cursor_template.write_text(mdc_content)
    rprint(f"[green]✅ Generated template: {cursor_template}[/green]")


def uninstall_symlinks(target_dir: Path, specific_system: Optional[str] = None) -> None:
    """Remove symlinks from target directory"""
    repo_root = get_repo_root()
    removed_count = 0

    # Determine which systems to process
    if specific_system:
        if specific_system not in AGENTIC_SYSTEMS:
            rprint(f"[red]Error: Unknown agentic system '{specific_system}'[/red]")
            return
        systems_to_check = {specific_system: AGENTIC_SYSTEMS[specific_system]}
    else:
        systems_to_check = AGENTIC_SYSTEMS

    for system_name, config in systems_to_check.items():
        target_path = target_dir / config["path"]
        expected_source = repo_root / config["source"]

        if target_path.is_symlink():
            try:
                if target_path.readlink() == expected_source:
                    target_path.unlink()
                    rprint(f"[green]✅ Removed {system_name} symlink: {target_path}[/green]")
                    removed_count += 1

                    # Clean up empty .cursor/rules directory
                    if system_name == "Cursor":
                        cursor_rules_dir = target_path.parent
                        cursor_dir = cursor_rules_dir.parent
                        try:
                            if cursor_rules_dir.exists() and not any(cursor_rules_dir.iterdir()):
                                cursor_rules_dir.rmdir()
                                rprint(f"[blue]Removed empty directory: {cursor_rules_dir}[/blue]")
                            if (
                                cursor_dir.exists()
                                and cursor_dir.name == ".cursor"
                                and not any(cursor_dir.iterdir())
                            ):
                                cursor_dir.rmdir()
                                rprint(f"[blue]Removed empty directory: {cursor_dir}[/blue]")
                        except OSError:
                            pass  # Directory not empty or other issue
                else:
                    rprint(f"[yellow]Skipping {target_path} (not our symlink)[/yellow]")
            except OSError as e:
                rprint(f"[red]Error removing symlink {target_path}: {e}[/red]")
        elif target_path.exists():
            rprint(f"[yellow]Skipping {target_path} (not a symlink)[/yellow]")

    if removed_count == 0:
        target_desc = f"for {specific_system}" if specific_system else ""
        rprint(f"[yellow]No symlinks found to remove {target_desc}[/yellow]")
    else:
        rprint(f"[green]Removed {removed_count} symlink(s)[/green]")


def ensure_templates_exist() -> None:
    """Ensure all required template files exist"""
    repo_root = get_repo_root()
    cursor_template = repo_root / "generated" / "cursor-agent.mdc"
    if not cursor_template.exists():
        rprint("[yellow]Generating missing templates...[/yellow]")
        generate_local_templates()


def create_symlinks(target_dir: Path, systems: list[str]) -> int:
    """Create symlinks for specified systems, returns count of created symlinks"""
    repo_root = get_repo_root()
    created_count = 0

    for sys in systems:
        config = AGENTIC_SYSTEMS[sys]
        target_path = target_dir / config["path"]
        source_path = repo_root / config["source"]

        if not source_path.exists():
            rprint(f"[red]{sys}: Source file not found: {source_path}[/red]")
            continue

        try:
            # Ensure parent directory exists (especially for Cursor)
            target_path.parent.mkdir(parents=True, exist_ok=True)

            if target_path.exists() or target_path.is_symlink():
                # Check if it's our existing symlink
                is_ours = target_path.is_symlink() and target_path.readlink() == source_path

                if is_ours:
                    rprint(f"[yellow]{sys}: Symlink already exists and points to correct location[/yellow]")
                    continue

                overwrite = Confirm.ask(f"{sys}: File {target_path} already exists. Overwrite?")
                if not overwrite:
                    rprint(f"[yellow]{sys}: Skipped[/yellow]")
                    continue

                target_path.unlink()

            target_path.symlink_to(source_path)
            rprint(f"[green]✅ {sys}: Created symlink: {target_path} → {source_path}[/green]")
            created_count += 1

        except OSError as e:
            rprint(f"[red]{sys}: Error creating symlink: {e}[/red]")

    return created_count


def validate_systems(systems: list[str]) -> None:
    """Validate that all specified systems are known"""
    for sys in systems:
        if sys not in AGENTIC_SYSTEMS:
            rprint(f"[red]Error: Unknown agentic system '{sys}'[/red]")
            rprint(f"Available systems: {', '.join(AGENTIC_SYSTEMS.keys())}")
            raise ValueError(f"Unknown system: {sys}")


def validate_source_files() -> None:
    """Validate that source AGENT.md file exists"""
    source_agent_md = get_source_agent_md()
    if not source_agent_md.exists():
        rprint(f"[red]Error: Source AGENT.md not found at {source_agent_md}[/red]")
        raise FileNotFoundError(f"Source AGENT.md not found: {source_agent_md}")


def get_commands_dir() -> Path:
    """Get the path to the commands directory in the repo"""
    return get_repo_root() / "commands" / "claude"


def install_commands(target_dir: Path) -> Dict[str, bool]:
    """Install slash commands to target project's .claude/commands/ directory.

    Returns a dict with installation results.
    """
    results = {
        "commands_installed": False,
        "commands_count": 0,
    }

    repo_commands_dir = get_commands_dir()
    if not repo_commands_dir.exists():
        rprint("[yellow]No commands directory found in repo[/yellow]")
        return results

    # Get all .md files in the commands directory
    command_files = list(repo_commands_dir.glob("*.md"))
    if not command_files:
        rprint("[yellow]No command files found[/yellow]")
        return results

    # Create target commands directory
    target_commands_dir = target_dir / ".claude" / "commands"
    target_commands_dir.mkdir(parents=True, exist_ok=True)

    installed_count = 0
    for cmd_file in command_files:
        target_path = target_commands_dir / cmd_file.name

        try:
            if target_path.exists() or target_path.is_symlink():
                # Check if it's our symlink
                if target_path.is_symlink() and target_path.readlink() == cmd_file:
                    rprint(f"[yellow]Command {cmd_file.name} already installed[/yellow]")
                    continue

                # File exists but isn't our symlink - ask to overwrite
                overwrite = Confirm.ask(f"Command {cmd_file.name} already exists. Overwrite?")
                if not overwrite:
                    rprint(f"[yellow]Skipping {cmd_file.name}[/yellow]")
                    continue
                target_path.unlink()

            target_path.symlink_to(cmd_file)
            rprint(f"[green]✅ Installed command: /{cmd_file.stem}[/green]")
            installed_count += 1

        except OSError as e:
            rprint(f"[red]Error installing command {cmd_file.name}: {e}[/red]")

    results["commands_installed"] = installed_count > 0
    results["commands_count"] = installed_count
    return results


def uninstall_commands(target_dir: Path) -> None:
    """Remove slash commands from target project's .claude/commands/ directory."""
    repo_commands_dir = get_commands_dir()
    target_commands_dir = target_dir / ".claude" / "commands"

    if not target_commands_dir.exists():
        return

    if not repo_commands_dir.exists():
        return

    # Get command files from repo to know which ones are ours
    command_files = list(repo_commands_dir.glob("*.md"))
    removed_count = 0

    for cmd_file in command_files:
        target_path = target_commands_dir / cmd_file.name

        if target_path.is_symlink():
            try:
                if target_path.readlink() == cmd_file:
                    target_path.unlink()
                    rprint(f"[green]✅ Removed command: /{cmd_file.stem}[/green]")
                    removed_count += 1
            except OSError as e:
                rprint(f"[red]Error removing command {cmd_file.name}: {e}[/red]")

    # Clean up empty directories
    try:
        if target_commands_dir.exists() and not any(target_commands_dir.iterdir()):
            target_commands_dir.rmdir()
            rprint(f"[blue]Removed empty directory: {target_commands_dir}[/blue]")

        claude_dir = target_commands_dir.parent
        if claude_dir.exists() and claude_dir.name == ".claude" and not any(claude_dir.iterdir()):
            claude_dir.rmdir()
            rprint(f"[blue]Removed empty directory: {claude_dir}[/blue]")
    except OSError:
        pass

    if removed_count > 0:
        rprint(f"[green]Removed {removed_count} command(s)[/green]")
