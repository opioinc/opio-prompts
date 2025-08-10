#!/usr/bin/env python3
# ABOUTME: Language-specific prompt setup for AI agents
# ABOUTME: Handles CLAUDE.md creation and language prompt symlinks

from pathlib import Path
from typing import List, Optional
import shutil

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
    language: str
) -> dict:
    """
    Setup language-specific prompts in the target directory
    
    Returns dict with status of operations:
    - prompts_dir_created: bool
    - language_symlink_created: bool
    - project_md_updated: bool
    """
    results = {
        "prompts_dir_created": False,
        "language_symlink_created": False,
        "project_md_updated": False
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
    
    return results


def uninstall_language_prompts(target_dir: Path, language: Optional[str] = None) -> None:
    """
    Remove language prompts setup from target directory
    
    If language is specified, only remove that language's symlink.
    Otherwise, remove the entire prompts directory.
    """
    prompts_dir = target_dir / "prompts"
    
    if not prompts_dir.exists():
        rprint(f"[yellow]No prompts directory found at {prompts_dir}[/yellow]")
        return
    
    if language:
        # Remove specific language symlink
        lang_symlink = prompts_dir / language
        if lang_symlink.is_symlink():
            lang_symlink.unlink()
            rprint(f"[green]✅ Removed {language} symlink from {prompts_dir}[/green]")
            
            # Update project.md to remove references
            update_project_md(target_dir, language, remove=True)
            
            # Check if prompts directory is now empty
            if not any(prompts_dir.iterdir()):
                prompts_dir.rmdir()
                rprint(f"[blue]Removed empty prompts directory[/blue]")
        elif lang_symlink.exists():
            rprint(f"[yellow]Warning: {lang_symlink} is not a symlink, skipping[/yellow]")
        else:
            rprint(f"[yellow]No {language} symlink found in {prompts_dir}[/yellow]")
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