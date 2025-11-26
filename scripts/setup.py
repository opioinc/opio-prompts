#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# dependencies = ["typer[all]", "rich"]
# ///

# ABOUTME: CLI interface for agent setup - creates symlinks to AGENT.md files
# ABOUTME: Lightweight wrapper around agent_setup module

from pathlib import Path
from typing import List, Optional

import typer
from rich import print as rprint
from rich.prompt import Prompt

from agent_setup import (
    AGENTIC_SYSTEMS,
    create_symlinks,
    ensure_templates_exist,
    generate_local_templates,
    install_commands,
    uninstall_commands,
    uninstall_symlinks,
    validate_source_files,
    validate_systems,
)
from language import (
    get_available_languages,
    setup_language_prompts,
    uninstall_language_prompts,
    validate_language,
)
from package import (
    get_available_packages,
    setup_package_prompts,
    uninstall_package_prompts,
    validate_package,
)

app = typer.Typer(help="Setup AGENT.md symlinks for agentic development systems")


@app.command()
def main(
    project_path: Optional[str] = typer.Argument(None, help="Path to the target project directory"),
    system: Optional[List[str]] = typer.Option(None, "--system", "-s", help="Agentic system(s) to use (can specify multiple)"),
    uninstall: bool = typer.Option(False, "--uninstall", "-u", help="Remove existing symlinks"),
    regenerate: bool = typer.Option(False, "--regenerate", "-r", help="Regenerate local template files"),
    add_language: bool = typer.Option(False, "--add-language", "-l", help="Add language-specific prompts to project (includes hooks by default)"),
    language: Optional[str] = typer.Option(None, "--language", help="Language to add (use with --add-language)"),
    no_hooks: bool = typer.Option(False, "--no-hooks", help="Skip hook installation when adding languages"),
    uninstall_language: bool = typer.Option(False, "--uninstall-language", help="Remove language prompts from project"),
    remove_language: bool = typer.Option(False, "--remove-language", help="Remove language prompts from project"),
    add_package: bool = typer.Option(False, "--add-package", "-p", help="Add package prompts to project"),
    package: Optional[str] = typer.Option(None, "--package", help="Package to add (use with --add-package)"),
    remove_package: bool = typer.Option(False, "--remove-package", help="Remove package prompts from project"),
):
    """Setup AGENT.md symlinks for agentic development systems"""

    # Handle regenerate mode
    if regenerate:
        generate_local_templates()
        return

    # Get project path
    if not project_path:
        project_path = Prompt.ask("Enter the target project directory path")

    target_dir = Path(project_path).expanduser().resolve()

    if not target_dir.exists():
        rprint(f"[red]Error: Directory {target_dir} does not exist[/red]")
        raise typer.Exit(1)

    if not target_dir.is_dir():
        rprint(f"[red]Error: {target_dir} is not a directory[/red]")
        raise typer.Exit(1)

    # Handle language mode
    if add_language:
        # Get language if not provided
        if not language:
            available = get_available_languages()
            if not available:
                rprint("[red]No languages found in lang/ directory[/red]")
                raise typer.Exit(1)
            
            rprint("\n[bold]Available languages:[/bold]")
            for i, lang in enumerate(available, 1):
                rprint(f"  {i}. {lang}")
            
            choice = Prompt.ask("Select a language (number)")
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(available):
                    language = available[idx]
                else:
                    rprint("[red]Invalid selection[/red]")
                    raise typer.Exit(1)
            except ValueError:
                rprint("[red]Invalid selection[/red]")
                raise typer.Exit(1)
        
        # Validate language
        if not validate_language(language):
            rprint(f"[red]Error: Language '{language}' not found[/red]")
            available = get_available_languages()
            if available:
                rprint(f"Available languages: {', '.join(available)}")
            raise typer.Exit(1)
        
        # Setup language prompts
        try:
            # Pass the install_hooks parameter (inverted from no_hooks flag)
            results = setup_language_prompts(target_dir, language, install_hooks=not no_hooks)
            
            # Summary
            if results["language_symlink_created"]:
                rprint(f"[blue]✨ Language prompts for {language} have been linked[/blue]")
            if results["project_md_updated"]:
                rprint(f"[blue]✨ project.md has been updated with {language} references[/blue]")
            if results.get("hooks_installed"):
                rprint(f"[blue]✨ Hooks have been installed for {language}[/blue]")
            elif no_hooks:
                rprint(f"[yellow]Hooks were skipped (--no-hooks flag)[/yellow]")
                
            rprint(f"\n[green]Language setup complete for {language} in {target_dir}[/green]")
            
        except Exception as e:
            rprint(f"[red]Error setting up language prompts: {e}[/red]")
            raise typer.Exit(1)
        
        return

    # Handle remove/uninstall language mode
    if uninstall_language or remove_language:
        # Get language if not provided
        if not language:
            available = get_available_languages()
            if not available:
                rprint("[red]No languages found in lang/ directory[/red]")
                raise typer.Exit(1)
            
            rprint("\n[bold]Available languages:[/bold]")
            for i, lang in enumerate(available, 1):
                rprint(f"  {i}. {lang}")
            
            choice = Prompt.ask("Select a language to remove (number)")
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(available):
                    language = available[idx]
                else:
                    rprint("[red]Invalid selection[/red]")
                    raise typer.Exit(1)
            except ValueError:
                rprint("[red]Invalid selection[/red]")
                raise typer.Exit(1)
        
        # Remove language prompts
        uninstall_language_prompts(target_dir, language)
        rprint(f"[green]Language {language} removed from {target_dir}[/green]")
        return

    # Handle package mode
    if add_package:
        # Get package if not provided
        if not package:
            available = get_available_packages()
            if not available:
                rprint("[red]No packages found in packages/ directory[/red]")
                raise typer.Exit(1)
            
            rprint("\n[bold]Available packages:[/bold]")
            for i, pkg in enumerate(available, 1):
                rprint(f"  {i}. {pkg}")
            
            choice = Prompt.ask("Select a package (number)")
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(available):
                    package = available[idx]
                else:
                    rprint("[red]Invalid selection[/red]")
                    raise typer.Exit(1)
            except ValueError:
                rprint("[red]Invalid selection[/red]")
                raise typer.Exit(1)
        
        # Validate package
        if not validate_package(package):
            rprint(f"[red]Error: Package '{package}' not found[/red]")
            available = get_available_packages()
            if available:
                rprint(f"Available packages: {', '.join(available)}")
            raise typer.Exit(1)
        
        # Setup package prompts
        try:
            results = setup_package_prompts(target_dir, package)
            
            # Summary
            if results["package_symlink_created"]:
                rprint(f"[blue]✨ Package prompts for {package} have been linked[/blue]")
            if results["project_md_updated"]:
                rprint(f"[blue]✨ project.md has been updated with {package} references[/blue]")
                
            rprint(f"\n[green]Package setup complete for {package} in {target_dir}[/green]")
            
        except Exception as e:
            rprint(f"[red]Error setting up package prompts: {e}[/red]")
            raise typer.Exit(1)
        
        return
    
    # Handle remove package mode
    if remove_package:
        # Get package if not provided
        if not package:
            available = get_available_packages()
            if not available:
                rprint("[red]No packages found in packages/ directory[/red]")
                raise typer.Exit(1)
            
            rprint("\n[bold]Available packages:[/bold]")
            for i, pkg in enumerate(available, 1):
                rprint(f"  {i}. {pkg}")
            
            choice = Prompt.ask("Select a package to remove (number)")
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(available):
                    package = available[idx]
                else:
                    rprint("[red]Invalid selection[/red]")
                    raise typer.Exit(1)
            except ValueError:
                rprint("[red]Invalid selection[/red]")
                raise typer.Exit(1)
        
        # Remove package prompts
        uninstall_package_prompts(target_dir, package)
        rprint(f"[green]Package {package} removed from {target_dir}[/green]")
        return

    # Handle uninstall mode
    if uninstall:
        # Remove agent system symlinks
        single_system = system[0] if system else None
        uninstall_symlinks(target_dir, single_system)

        # Also remove language prompts and commands if no specific system was specified
        if not single_system:
            uninstall_language_prompts(target_dir)
            uninstall_commands(target_dir)
        elif single_system == "Claude Code":
            # If specifically uninstalling Claude Code, also remove its commands
            uninstall_commands(target_dir)

        return

    # Get agentic systems
    if not system:
        rprint("\n[bold]Available agentic systems:[/bold]")
        for i, sys_name in enumerate(AGENTIC_SYSTEMS.keys(), 1):
            rprint(f"  {i}. {sys_name}")

        rprint("\n[bold]Select systems to install (space-separated numbers, e.g., '1 3' for Claude Code and Cursor):[/bold]")
        choices_input = Prompt.ask("Enter your choices")

        try:
            selected_indices = [int(x.strip()) for x in choices_input.split()]
            system_names = list(AGENTIC_SYSTEMS.keys())
            system = [system_names[i - 1] for i in selected_indices if 1 <= i <= len(system_names)]

            if not system:
                rprint("[red]No valid systems selected[/red]")
                raise typer.Exit(1)

        except (ValueError, IndexError):
            rprint("[red]Invalid selection. Please enter numbers separated by spaces.[/red]")
            raise typer.Exit(1)

    # Validate inputs
    try:
        validate_systems(system)
        validate_source_files()
    except (ValueError, FileNotFoundError):
        raise typer.Exit(1)

    # Ensure templates exist
    ensure_templates_exist()

    # Create symlinks
    created_count = create_symlinks(target_dir, system)

    # Install slash commands for Claude Code
    if "Claude Code" in system:
        cmd_results = install_commands(target_dir)
        if cmd_results["commands_installed"]:
            rprint(f"[blue]✨ Installed {cmd_results['commands_count']} slash command(s)[/blue]")

    if created_count > 0:
        rprint(f"\n[blue]Successfully created {created_count} symlink(s)[/blue]")


if __name__ == "__main__":
    app()
