#!/usr/bin/env python3
# ABOUTME: Package-specific prompt setup for AI agents
# ABOUTME: Handles package symlinks and project.md amendments

from pathlib import Path
from typing import List, Optional
import shutil

from rich import print as rprint
from rich.prompt import Confirm


def get_repo_root() -> Path:
    """Get the path to the repository root"""
    script_dir = Path(__file__).parent
    return script_dir.parent


def get_available_packages() -> List[str]:
    """Get list of available packages from the packages directory"""
    packages_dir = get_repo_root() / "packages"
    if not packages_dir.exists():
        return []
    
    packages = []
    for item in packages_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            packages.append(item.name)
    
    return sorted(packages)


def validate_package(package: str) -> bool:
    """Validate that the specified package exists"""
    available = get_available_packages()
    return package in available


def get_package_files(package: str) -> List[str]:
    """Get list of markdown files in the package directory"""
    packages_dir = get_repo_root() / "packages" / package
    if not packages_dir.exists():
        return []
    
    files = []
    for item in packages_dir.iterdir():
        if item.is_file() and item.suffix == '.md':
            files.append(item.name)
    
    # Sort with core.md first if it exists
    if 'core.md' in files:
        files.remove('core.md')
        files = ['core.md'] + sorted(files)
    else:
        files = sorted(files)
    
    return files


def update_project_md(target_dir: Path, package: str, remove: bool = False) -> bool:
    """
    Update project.md file with package links
    
    Args:
        target_dir: The target project directory
        package: The package name
        remove: If True, remove the package links; if False, add them
    
    Returns:
        True if the file was modified, False if no changes were needed
    """
    project_md = target_dir / "project.md"
    
    # Get package files
    package_files = get_package_files(package)
    if not package_files:
        return False
    
    # Generate the lines to add/remove
    package_lines = [f"@prompts/{package}/{file}" for file in package_files]
    
    # Read existing content if file exists
    existing_lines = []
    if project_md.exists():
        existing_lines = project_md.read_text().splitlines()
    
    if remove:
        # Remove package lines
        original_count = len(existing_lines)
        existing_lines = [line for line in existing_lines if line not in package_lines]
        
        if len(existing_lines) == original_count:
            rprint(f"[yellow]No {package} references found in project.md[/yellow]")
            return False
        
        # Write back the modified content
        project_md.write_text('\n'.join(existing_lines) + '\n' if existing_lines else '')
        rprint(f"[green]✅ Removed {package} references from project.md[/green]")
        return True
    else:
        # Add package lines (idempotent - only add if not present)
        lines_to_add = []
        for line in package_lines:
            if line not in existing_lines:
                lines_to_add.append(line)
        
        if not lines_to_add:
            rprint(f"[yellow]All {package} references already exist in project.md[/yellow]")
            return False
        
        # Append the new lines
        all_lines = existing_lines + lines_to_add
        
        # Create or update the file
        project_md.write_text('\n'.join(all_lines) + '\n')
        rprint(f"[green]✅ Added {len(lines_to_add)} {package} reference(s) to project.md[/green]")
        return True


def setup_package_prompts(
    target_dir: Path,
    package: str
) -> dict:
    """
    Setup package-specific prompts in the target directory
    
    Returns dict with status of operations:
    - prompts_dir_created: bool
    - package_symlink_created: bool
    - project_md_updated: bool
    """
    results = {
        "prompts_dir_created": False,
        "package_symlink_created": False,
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
    
    # Step 2: Create symlink to package directory
    source_package_dir = repo_root / "packages" / package
    target_package_symlink = prompts_dir / package
    
    if not source_package_dir.exists():
        rprint(f"[red]Error: Package directory not found: {source_package_dir}[/red]")
        raise FileNotFoundError(f"Package directory not found: {source_package_dir}")
    
    if target_package_symlink.exists() or target_package_symlink.is_symlink():
        # Check if it's already the correct symlink
        if target_package_symlink.is_symlink() and target_package_symlink.readlink() == source_package_dir:
            rprint(f"[yellow]Package symlink for {package} already exists and is correct[/yellow]")
        else:
            overwrite = Confirm.ask(f"Symlink {target_package_symlink} already exists. Overwrite?")
            if not overwrite:
                rprint(f"[yellow]Skipped creating package symlink[/yellow]")
            else:
                if target_package_symlink.is_symlink():
                    target_package_symlink.unlink()
                else:
                    # It's a real directory/file, be more careful
                    rprint(f"[red]Warning: {target_package_symlink} is not a symlink[/red]")
                    if not Confirm.ask("This will remove a real file/directory. Continue?"):
                        rprint(f"[yellow]Aborted[/yellow]")
                    else:
                        if target_package_symlink.is_dir():
                            shutil.rmtree(target_package_symlink)
                        else:
                            target_package_symlink.unlink()
                        
                        target_package_symlink.symlink_to(source_package_dir)
                        rprint(f"[green]✅ Created symlink: {target_package_symlink} → {source_package_dir}[/green]")
                        results["package_symlink_created"] = True
    else:
        target_package_symlink.symlink_to(source_package_dir)
        rprint(f"[green]✅ Created symlink: {target_package_symlink} → {source_package_dir}[/green]")
        results["package_symlink_created"] = True
    
    # Step 3: Update project.md if it exists or create it
    if update_project_md(target_dir, package, remove=False):
        results["project_md_updated"] = True
    
    return results


def uninstall_package_prompts(target_dir: Path, package: Optional[str] = None) -> None:
    """
    Remove package prompts setup from target directory
    
    If package is specified, only remove that package's symlink and references.
    Otherwise, remove all package symlinks.
    """
    prompts_dir = target_dir / "prompts"
    
    if not prompts_dir.exists():
        rprint(f"[yellow]No prompts directory found at {prompts_dir}[/yellow]")
        return
    
    if package:
        # Remove specific package symlink
        package_symlink = prompts_dir / package
        if package_symlink.is_symlink():
            package_symlink.unlink()
            rprint(f"[green]✅ Removed {package} symlink from {prompts_dir}[/green]")
            
            # Update project.md to remove references
            update_project_md(target_dir, package, remove=True)
            
            # Check if prompts directory is now empty
            if not any(prompts_dir.iterdir()):
                prompts_dir.rmdir()
                rprint(f"[blue]Removed empty prompts directory[/blue]")
        elif package_symlink.exists():
            rprint(f"[yellow]Warning: {package_symlink} is not a symlink, skipping[/yellow]")
        else:
            rprint(f"[yellow]No {package} symlink found in {prompts_dir}[/yellow]")
    else:
        # Remove all package symlinks that point to our packages directory
        repo_root = get_repo_root()
        packages_dir = repo_root / "packages"
        
        for item in prompts_dir.iterdir():
            if item.is_symlink():
                try:
                    target = item.readlink()
                    if packages_dir in target.parents:
                        item.unlink()
                        rprint(f"[green]✅ Removed package symlink: {item}[/green]")
                        # Update project.md to remove references
                        update_project_md(target_dir, item.name, remove=True)
                except OSError:
                    pass


def list_package_setups(target_dir: Path) -> List[str]:
    """List packages currently set up in the target directory"""
    prompts_dir = target_dir / "prompts"
    if not prompts_dir.exists():
        return []
    
    packages = []
    for item in prompts_dir.iterdir():
        if item.is_symlink():
            # Check if it points to our packages directory
            try:
                target = item.readlink()
                repo_root = get_repo_root()
                packages_dir = repo_root / "packages"
                if packages_dir in target.parents:
                    packages.append(item.name)
            except OSError:
                pass
    
    return sorted(packages)