#!/usr/bin/env python3
"""Test script for hook installation functionality"""

from pathlib import Path
import tempfile
import json
import shutil
from rich import print as rprint

# Import the language module
import sys
sys.path.insert(0, str(Path(__file__).parent))
from language import (
    setup_language_prompts,
    uninstall_language_prompts,
    check_hook_dependencies,
    get_hook_config
)


def test_hook_installation():
    """Test installing and uninstalling hooks"""
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        rprint(f"\n[bold blue]Testing in directory: {test_dir}[/bold blue]\n")
        
        # Test 1: Check Python hook dependencies
        rprint("[bold]Test 1: Checking Python hook dependencies[/bold]")
        deps_ok, missing = check_hook_dependencies("python")
        if deps_ok:
            rprint("[green]✅ All Python dependencies satisfied[/green]")
        else:
            rprint(f"[yellow]⚠️ Missing dependencies: {missing}[/yellow]")
        
        # Test 2: Get Python hook configuration
        rprint("\n[bold]Test 2: Reading Python hook configuration[/bold]")
        config = get_hook_config("python")
        if config:
            rprint(f"[green]✅ Found Python hook config for agent: {config.get('agent')}[/green]")
            rprint(f"   Files to copy: {config.get('files', [])}")
        else:
            rprint("[red]❌ No Python hook configuration found[/red]")
        
        # Test 3: Install Python with hooks
        rprint("\n[bold]Test 3: Installing Python language with hooks[/bold]")
        results = setup_language_prompts(test_dir, "python")
        rprint(f"Results: {results}")
        
        # Verify hook files were copied
        hooks_dir = test_dir / "hooks" / "claude"
        if hooks_dir.exists():
            rprint(f"[green]✅ Hooks directory created: {hooks_dir}[/green]")
            hook_files = list(hooks_dir.iterdir())
            rprint(f"   Hook files: {[f.name for f in hook_files]}")
        else:
            rprint("[red]❌ Hooks directory not created[/red]")
        
        # Verify settings.json was created
        settings_file = test_dir / ".claude" / "settings.json"
        if settings_file.exists():
            rprint(f"[green]✅ Settings file created: {settings_file}[/green]")
            with open(settings_file) as f:
                settings = json.load(f)
                if "hooks" in settings:
                    rprint("   Hooks configured in settings.json")
                    rprint(f"   Hook types: {list(settings['hooks'].keys())}")
        else:
            rprint("[red]❌ Settings file not created[/red]")
        
        # Test 4: Install TypeScript hooks (if dependencies available)
        rprint("\n[bold]Test 4: Checking TypeScript hook dependencies[/bold]")
        ts_deps_ok, ts_missing = check_hook_dependencies("typescript")
        if ts_deps_ok:
            rprint("[green]✅ All TypeScript dependencies satisfied[/green]")
            rprint("\n[bold]Installing TypeScript language with hooks[/bold]")
            ts_results = setup_language_prompts(test_dir, "typescript")
            rprint(f"Results: {ts_results}")
            
            # Check if both hooks are in settings
            if settings_file.exists():
                with open(settings_file) as f:
                    settings = json.load(f)
                    if "hooks" in settings and "PostToolUse" in settings["hooks"]:
                        hook_count = len(settings["hooks"]["PostToolUse"])
                        rprint(f"[green]✅ Total hooks in settings: {hook_count}[/green]")
        else:
            rprint(f"[yellow]⚠️ Missing TypeScript dependencies: {ts_missing}[/yellow]")
            rprint("[yellow]Skipping TypeScript installation[/yellow]")
        
        # Test 5: Uninstall Python hooks
        rprint("\n[bold]Test 5: Uninstalling Python hooks[/bold]")
        uninstall_language_prompts(test_dir, "python")
        
        # Verify Python hook files were removed
        if hooks_dir.exists():
            remaining_files = list(hooks_dir.glob("python-*"))
            if not remaining_files:
                rprint("[green]✅ Python hook files removed[/green]")
            else:
                rprint(f"[red]❌ Python hook files still exist: {remaining_files}[/red]")
        
        # Verify settings were updated
        if settings_file.exists():
            with open(settings_file) as f:
                settings = json.load(f)
                rprint(f"   Remaining hooks in settings: {settings.get('hooks', {})}")
        
        rprint("\n[bold green]✅ Hook installation tests completed![/bold green]")
        
        # Show final directory structure
        rprint("\n[bold]Final directory structure:[/bold]")
        for root, dirs, files in test_dir.walk():
            level = root.relative_to(test_dir).parts
            indent = "  " * len(level)
            rprint(f"{indent}{root.name}/")
            subindent = "  " * (len(level) + 1)
            for file in files:
                rprint(f"{subindent}{file}")


if __name__ == "__main__":
    test_hook_installation()