#!/usr/bin/env python3
# ABOUTME: Language-specific prompt setup for AI agents
# ABOUTME: Handles CLAUDE.md creation and language prompt symlinks

from pathlib import Path
from typing import List, Optional, Dict, Any
import shutil
import json
import subprocess

from rich import print as rprint
from rich.prompt import Confirm


def get_repo_root() -> Path:
    """Get the path to the repository root"""
    script_dir = Path(__file__).parent
    return script_dir.parent


def get_available_languages() -> List[str]:
    """Get list of available languages from the lang directory"""
    lang_dir = get_repo_root() / "lang"
    if not lang_dir.exists():
        return []
    
    languages = []
    for item in lang_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            languages.append(item.name)
    
    return sorted(languages)


def validate_language(language: str) -> bool:
    """Validate that the specified language exists"""
    available = get_available_languages()
    return language in available


def get_language_files(language: str) -> List[str]:
    """Get list of markdown files in the language directory"""
    lang_dir = get_repo_root() / "lang" / language
    if not lang_dir.exists():
        return []
    
    files = []
    for item in lang_dir.iterdir():
        if item.is_file() and item.suffix == '.md':
            files.append(item.name)
    
    # Sort with core.md first if it exists
    if 'core.md' in files:
        files.remove('core.md')
        files = ['core.md'] + sorted(files)
    else:
        files = sorted(files)
    
    return files


def update_project_md(target_dir: Path, language: str, remove: bool = False) -> bool:
    """
    Update project.md file with language links
    
    Args:
        target_dir: The target project directory
        language: The language name
        remove: If True, remove the language links; if False, add them
    
    Returns:
        True if the file was modified, False if no changes were needed
    """
    project_md = target_dir / "project.md"
    
    # Get language files
    language_files = get_language_files(language)
    if not language_files:
        return False
    
    # Generate the lines to add/remove
    language_lines = [f"@prompts/{language}/{file}" for file in language_files]
    
    # Read existing content if file exists
    existing_lines = []
    if project_md.exists():
        existing_lines = project_md.read_text().splitlines()
    
    if remove:
        # Remove language lines
        original_count = len(existing_lines)
        existing_lines = [line for line in existing_lines if line not in language_lines]
        
        if len(existing_lines) == original_count:
            rprint(f"[yellow]No {language} references found in project.md[/yellow]")
            return False
        
        # Write back the modified content
        project_md.write_text('\n'.join(existing_lines) + '\n' if existing_lines else '')
        rprint(f"[green]✅ Removed {language} references from project.md[/green]")
        return True
    else:
        # Add language lines (idempotent - only add if not present)
        lines_to_add = []
        for line in language_lines:
            if line not in existing_lines:
                lines_to_add.append(line)
        
        if not lines_to_add:
            rprint(f"[yellow]All {language} references already exist in project.md[/yellow]")
            return False
        
        # Append the new lines
        all_lines = existing_lines + lines_to_add
        
        # Create or update the file
        project_md.write_text('\n'.join(all_lines) + '\n')
        rprint(f"[green]✅ Added {len(lines_to_add)} {language} reference(s) to project.md[/green]")
        return True


def setup_language_prompts(
    target_dir: Path,
    language: str,
    agent: str = "claude"
) -> dict:
    """
    Setup language-specific prompts in the target directory
    
    Returns dict with status of operations:
    - prompts_dir_created: bool
    - language_symlink_created: bool
    - project_md_updated: bool
    - hooks_installed: bool
    """
    results = {
        "prompts_dir_created": False,
        "language_symlink_created": False,
        "project_md_updated": False,
        "hooks_installed": False
    }
    
    repo_root = get_repo_root()
    
    # Step 1: Create prompts directory
    prompts_dir = target_dir / "prompts"
    if not prompts_dir.exists():
        prompts_dir.mkdir(parents=True, exist_ok=True)
        rprint(f"[green]✅ Created prompts directory at {prompts_dir}[/green]")
        results["prompts_dir_created"] = True
    else:
        rprint(f"[blue]Prompts directory already exists at {prompts_dir}[/blue]")
    
    # Step 2: Create symlink to language directory
    source_lang_dir = repo_root / "lang" / language
    target_lang_symlink = prompts_dir / language
    
    if not source_lang_dir.exists():
        rprint(f"[red]Error: Language directory not found: {source_lang_dir}[/red]")
        raise FileNotFoundError(f"Language directory not found: {source_lang_dir}")
    
    if target_lang_symlink.exists() or target_lang_symlink.is_symlink():
        # Check if it's already the correct symlink
        if target_lang_symlink.is_symlink() and target_lang_symlink.readlink() == source_lang_dir:
            rprint(f"[yellow]Language symlink for {language} already exists and is correct[/yellow]")
            # Still try to install hooks even if symlink exists
            if setup_language_hooks(target_dir, language, agent):
                results["hooks_installed"] = True
            return results
        
        overwrite = Confirm.ask(f"Symlink {target_lang_symlink} already exists. Overwrite?")
        if not overwrite:
            rprint(f"[yellow]Skipped creating language symlink[/yellow]")
            return results
        
        if target_lang_symlink.is_symlink():
            target_lang_symlink.unlink()
        else:
            # It's a real directory/file, be more careful
            rprint(f"[red]Warning: {target_lang_symlink} is not a symlink[/red]")
            if not Confirm.ask("This will remove a real file/directory. Continue?"):
                rprint(f"[yellow]Aborted[/yellow]")
                return results
            if target_lang_symlink.is_dir():
                shutil.rmtree(target_lang_symlink)
            else:
                target_lang_symlink.unlink()
    
    target_lang_symlink.symlink_to(source_lang_dir)
    rprint(f"[green]✅ Created symlink: {target_lang_symlink} → {source_lang_dir}[/green]")
    results["language_symlink_created"] = True
    
    # Step 3: Update project.md if it exists or create it
    if update_project_md(target_dir, language, remove=False):
        results["project_md_updated"] = True
    
    # Step 4: Install hooks for the language
    if setup_language_hooks(target_dir, language, agent):
        results["hooks_installed"] = True
    
    return results


def uninstall_language_prompts(target_dir: Path, language: Optional[str] = None, agent: str = "claude") -> None:
    """
    Remove language prompts setup from target directory
    
    If language is specified, only remove that language's symlink and hooks.
    Otherwise, remove the entire prompts directory and all hooks.
    """
    prompts_dir = target_dir / "prompts"
    
    if not prompts_dir.exists():
        rprint(f"[yellow]No prompts directory found at {prompts_dir}[/yellow]")
        # Still try to remove hooks even if prompts don't exist
        if language:
            remove_language_hooks(target_dir, language, agent)
        return
    
    if language:
        # Remove specific language symlink
        lang_symlink = prompts_dir / language
        if lang_symlink.is_symlink():
            lang_symlink.unlink()
            rprint(f"[green]✅ Removed {language} symlink from {prompts_dir}[/green]")
            
            # Update project.md to remove references
            update_project_md(target_dir, language, remove=True)
            
            # Remove hooks for this language
            remove_language_hooks(target_dir, language, agent)
            
            # Check if prompts directory is now empty
            if not any(prompts_dir.iterdir()):
                prompts_dir.rmdir()
                rprint(f"[blue]Removed empty prompts directory[/blue]")
        elif lang_symlink.exists():
            rprint(f"[yellow]Warning: {lang_symlink} is not a symlink, skipping[/yellow]")
        else:
            rprint(f"[yellow]No {language} symlink found in {prompts_dir}[/yellow]")
            # Still try to remove hooks
            remove_language_hooks(target_dir, language, agent)
    else:
        # Remove all language symlinks that point to our lang directory
        repo_root = get_repo_root()
        lang_dir = repo_root / "lang"
        
        for item in prompts_dir.iterdir():
            if item.is_symlink():
                try:
                    target = item.readlink()
                    if lang_dir in target.parents:
                        item.unlink()
                        rprint(f"[green]✅ Removed language symlink: {item}[/green]")
                        # Update project.md to remove references
                        update_project_md(target_dir, item.name, remove=True)
                        # Remove hooks for this language
                        remove_language_hooks(target_dir, item.name, agent)
                except OSError:
                    pass


def list_language_setups(target_dir: Path) -> List[str]:
    """List languages currently set up in the target directory"""
    prompts_dir = target_dir / "prompts"
    if not prompts_dir.exists():
        return []
    
    languages = []
    for item in prompts_dir.iterdir():
        if item.is_symlink():
            # Check if it points to our lang directory
            try:
                target = item.readlink()
                repo_root = get_repo_root()
                lang_dir = repo_root / "lang"
                if lang_dir in target.parents:
                    languages.append(item.name)
            except OSError:
                pass
    
    return sorted(languages)


def check_hook_dependencies(language: str, agent: str = "claude") -> tuple[bool, List[str]]:
    """
    Check if required dependencies for hooks are installed
    
    Returns:
        Tuple of (all_satisfied, missing_dependencies)
    """
    repo_root = get_repo_root()
    config_file = repo_root / "lang" / language / "hooks" / f"{agent}.json"
    
    if not config_file.exists():
        return True, []  # No hooks config means no dependencies to check
    
    try:
        with open(config_file) as f:
            config = json.load(f)
    except (json.JSONDecodeError, IOError):
        rprint(f"[yellow]Warning: Could not read hook config from {config_file}[/yellow]")
        return True, []
    
    missing = []
    dependencies = config.get("dependencies", {})
    
    # Check required commands
    for cmd in dependencies.get("commands", []):
        result = subprocess.run(
            ["which", cmd],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            missing.append(cmd)
    
    # Check optional commands (at least one should exist)
    optional_cmds = dependencies.get("optional_commands", [])
    if optional_cmds:
        found_any = False
        for cmd in optional_cmds:
            result = subprocess.run(
                ["which", cmd],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                found_any = True
                break
        if not found_any:
            missing.append(f"one of: {', '.join(optional_cmds)}")
    
    # For Python packages, we just note them but don't fail
    # (they might be in the project's virtual environment)
    python_packages = dependencies.get("python_packages", [])
    if python_packages and language == "python":
        rprint(f"[blue]Note: Python packages required: {', '.join(python_packages)}[/blue]")
    
    return len(missing) == 0, missing


def get_hook_config(language: str, agent: str = "claude") -> Optional[Dict[str, Any]]:
    """Read agent-specific hook configuration"""
    repo_root = get_repo_root()
    config_file = repo_root / "lang" / language / "hooks" / f"{agent}.json"
    
    if not config_file.exists():
        return None
    
    try:
        with open(config_file) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        rprint(f"[red]Error reading hook config: {e}[/red]")
        return None


def copy_hook_files(language: str, target_dir: Path, agent: str = "claude") -> bool:
    """
    Copy hook files to target_project/hooks/{agent}/
    
    Returns:
        True if files were copied successfully
    """
    repo_root = get_repo_root()
    source_hooks_dir = repo_root / "lang" / language / "hooks"
    
    # Get hook configuration to know which files to copy
    config = get_hook_config(language, agent)
    if not config:
        return True  # No hooks to copy
    
    files_to_copy = config.get("files", [])
    if not files_to_copy:
        return True  # No files specified
    
    # Create target hooks directory
    target_hooks_dir = target_dir / "hooks" / agent
    target_hooks_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy each file
    for file_name in files_to_copy:
        source_file = source_hooks_dir / file_name
        target_file = target_hooks_dir / file_name
        
        if not source_file.exists():
            rprint(f"[yellow]Warning: Hook file not found: {source_file}[/yellow]")
            continue
        
        # Copy file (preserving permissions for scripts)
        shutil.copy2(source_file, target_file)
        
        # Make shell scripts executable
        if file_name.endswith('.sh') or file_name.endswith('.py'):
            target_file.chmod(target_file.stat().st_mode | 0o111)
        
        rprint(f"[green]✅ Copied hook: {file_name}[/green]")
    
    return True


def update_claude_settings(target_dir: Path, language: str, remove: bool = False) -> bool:
    """
    Update .claude/settings.json with hook configuration
    
    Args:
        target_dir: The target project directory
        language: The language name
        remove: If True, remove hooks; if False, add them
    
    Returns:
        True if settings were updated successfully
    """
    # Get hook configuration
    config = get_hook_config(language, "claude")
    if not config:
        return True  # No hooks to configure
    
    # Create .claude directory if needed
    claude_dir = target_dir / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)
    
    settings_file = claude_dir / "settings.json"
    
    # Read existing settings
    existing_settings = {}
    if settings_file.exists():
        try:
            with open(settings_file) as f:
                existing_settings = json.load(f)
        except (json.JSONDecodeError, IOError):
            rprint(f"[yellow]Warning: Could not read existing settings.json[/yellow]")
    
    if remove:
        # Remove hooks for this language
        if "hooks" not in existing_settings:
            return True  # Nothing to remove
        
        # Remove hooks that match our language's configuration
        hooks_config = config.get("hooks", {})
        for hook_type, hook_list in hooks_config.items():
            if hook_type in existing_settings["hooks"]:
                # Filter out hooks that match our command patterns
                for hook_entry in hook_list:
                    matcher = hook_entry.get("matcher")
                    if matcher:
                        existing_settings["hooks"][hook_type] = [
                            h for h in existing_settings["hooks"][hook_type]
                            if h.get("matcher") != matcher
                        ]
        
        # Clean up empty hook sections
        existing_settings["hooks"] = {
            k: v for k, v in existing_settings["hooks"].items() if v
        }
        if not existing_settings["hooks"]:
            del existing_settings["hooks"]
        
        rprint(f"[green]✅ Removed {language} hooks from settings.json[/green]")
    else:
        # Add hooks for this language
        hooks_to_add = config.get("hooks", {})
        
        if "hooks" not in existing_settings:
            existing_settings["hooks"] = {}
        
        # Check for existing hooks and warn
        has_existing = False
        for hook_type, hook_list in hooks_to_add.items():
            if hook_type in existing_settings["hooks"] and existing_settings["hooks"][hook_type]:
                has_existing = True
                break
        
        if has_existing:
            rprint(f"[yellow]Warning: Existing hooks found in settings.json[/yellow]")
            rprint(f"[yellow]Adding {language} hooks additively (existing hooks preserved)[/yellow]")
        
        # Merge hooks additively
        for hook_type, hook_list in hooks_to_add.items():
            if hook_type not in existing_settings["hooks"]:
                existing_settings["hooks"][hook_type] = []
            
            # Add new hooks (avoid duplicates based on matcher)
            for new_hook in hook_list:
                # Check if a hook with the same matcher already exists
                matcher = new_hook.get("matcher")
                exists = any(
                    h.get("matcher") == matcher 
                    for h in existing_settings["hooks"][hook_type]
                )
                if not exists:
                    existing_settings["hooks"][hook_type].append(new_hook)
        
        rprint(f"[green]✅ Added {language} hooks to settings.json[/green]")
    
    # Write updated settings
    with open(settings_file, 'w') as f:
        json.dump(existing_settings, f, indent=2)
        f.write('\n')
    
    return True


def setup_language_hooks(target_dir: Path, language: str, agent: str = "claude") -> bool:
    """
    Setup hooks for a language in the target directory
    
    Returns:
        True if hooks were set up successfully
    """
    # Check if hooks exist for this language
    config = get_hook_config(language, agent)
    if not config:
        rprint(f"[blue]No {agent} hooks configured for {language}[/blue]")
        return True
    
    # Check dependencies
    deps_ok, missing = check_hook_dependencies(language, agent)
    if not deps_ok:
        rprint(f"[red]Error: Missing dependencies for {language} hooks:[/red]")
        for dep in missing:
            rprint(f"[red]  - {dep}[/red]")
        rprint(f"[yellow]Please install missing dependencies before continuing[/yellow]")
        return False
    
    # Copy hook files
    if not copy_hook_files(language, target_dir, agent):
        return False
    
    # Update agent settings
    if agent == "claude":
        if not update_claude_settings(target_dir, language, remove=False):
            return False
    # Add other agents here in the future
    
    rprint(f"[green]✅ Hooks installed for {language}[/green]")
    return True


def remove_language_hooks(target_dir: Path, language: str, agent: str = "claude") -> bool:
    """
    Remove hooks for a language from the target directory
    
    Returns:
        True if hooks were removed successfully
    """
    # Get hook configuration to know which files to remove
    config = get_hook_config(language, agent)
    if not config:
        return True  # No hooks to remove
    
    # Remove hook files
    target_hooks_dir = target_dir / "hooks" / agent
    if target_hooks_dir.exists():
        files_to_remove = config.get("files", [])
        for file_name in files_to_remove:
            target_file = target_hooks_dir / file_name
            if target_file.exists():
                target_file.unlink()
                rprint(f"[green]✅ Removed hook: {file_name}[/green]")
        
        # Remove directory if empty
        if not any(target_hooks_dir.iterdir()):
            target_hooks_dir.rmdir()
            rprint(f"[blue]Removed empty {agent} hooks directory[/blue]")
        
        # Remove hooks directory if empty
        hooks_dir = target_dir / "hooks"
        if hooks_dir.exists() and not any(hooks_dir.iterdir()):
            hooks_dir.rmdir()
            rprint(f"[blue]Removed empty hooks directory[/blue]")
    
    # Update agent settings
    if agent == "claude":
        update_claude_settings(target_dir, language, remove=True)
    # Add other agents here in the future
    
    rprint(f"[green]✅ Hooks removed for {language}[/green]")
    return True