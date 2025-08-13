#!/usr/bin/env node
// ABOUTME: TypeScript/Svelte hook for Claude Code that runs pnpm check (svelte-check) on saved files
// ABOUTME: Blocks further operations if type checking fails, ensuring LLM changes are compliant

import { execSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';

// Use process.cwd() for the script directory since we're running from project root
const __dirname = path.dirname(process.argv[1] || process.cwd());

// Types for Claude Code hook interface
interface ClaudeHookInput {
  session_id?: string;
  transcript_path?: string;
  cwd?: string;
  hook_event_name?: string;
  tool_name: string;
  tool_input: {
    file_path?: string;
    [key: string]: unknown;
  };
  [key: string]: unknown;
}

interface HookResponse {
  target?: string;
  tool?: string;
  success?: boolean;
  skipped?: boolean;
  reason?: string;
  decision?: 'block' | 'allow';
  error?: string;
  svelte_check?: {
    exit_code: number;
    error_count: number;
    warning_count: number;
    output?: string;
  };
  eslint?: {
    exit_code: number;
    error_count: number;
    warning_count: number;
    output?: string;
  };
}

// Logging setup
const SCRIPT_DIR = __dirname;
const LOG_DIR = path.join(SCRIPT_DIR, 'logs');
const LOG_FILE = path.join(LOG_DIR, `typescript-on-save-${new Date().toISOString().split('T')[0]}.log`);

// Ensure log directory exists
if (!fs.existsSync(LOG_DIR)) {
  fs.mkdirSync(LOG_DIR, { recursive: true });
}

function log(level: string, message: string): void {
  const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
  const logMessage = `${timestamp} | ${level} | ${message}\n`;
  fs.appendFileSync(LOG_FILE, logMessage);
}

function isTypeScriptOrSvelteFile(filePath: string): boolean {
  return /\.(ts|tsx|js|jsx|svelte)$/.test(filePath);
}

// Cache for dependency checks (valid for 5 minutes)
let dependencyCheckCache: { timestamp: number; result: { hasErrors: boolean; message?: string } } | null = null;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

function checkDependencies(): { hasErrors: boolean; message?: string } {
  // Return cached result if still valid
  if (dependencyCheckCache && (Date.now() - dependencyCheckCache.timestamp) < CACHE_DURATION) {
    log('DEBUG', 'Using cached dependency check result');
    return dependencyCheckCache.result;
  }
  
  // Check if pnpm is installed
  try {
    execSync('which pnpm', { stdio: 'ignore' });
  } catch {
    const result = {
      hasErrors: true,
      message: `
❌ pnpm is not installed!

To install pnpm, run one of the following:
  • npm install -g pnpm
  • curl -fsSL https://get.pnpm.io/install.sh | sh -
  • brew install pnpm (on macOS)

For more installation options, visit: https://pnpm.io/installation
`
    };
    dependencyCheckCache = { timestamp: Date.now(), result };
    return result;
  }

  // Check if svelte-check is installed
  try {
    execSync('pnpm list svelte-check --depth=0', { stdio: 'ignore', cwd: process.cwd() });
  } catch {
    const result = {
      hasErrors: true,
      message: `
❌ svelte-check is not installed in this project!

To install the required dependencies, run:
  pnpm install

Or specifically install svelte-check:
  pnpm add -D svelte-check

Make sure you're in the project root directory when running these commands.
`
    };
    dependencyCheckCache = { timestamp: Date.now(), result };
    return result;
  }

  // Check if eslint is installed
  try {
    execSync('pnpm list eslint --depth=0', { stdio: 'ignore', cwd: process.cwd() });
  } catch {
    const result = {
      hasErrors: true,
      message: `
❌ eslint is not installed in this project!

To install the required dependencies, run:
  pnpm install

Or specifically install eslint:
  pnpm add -D eslint

Make sure you're in the project root directory when running these commands.
`
    };
    dependencyCheckCache = { timestamp: Date.now(), result };
    return result;
  }

  const result = { hasErrors: false };
  // Cache the successful result
  dependencyCheckCache = { timestamp: Date.now(), result };
  return result;
}

function processTarget(target: string): HookResponse {
  log('INFO', `Processing target: ${target}`);
  
  // Check dependencies first
  const depCheck = checkDependencies();
  if (depCheck.hasErrors) {
    console.error(depCheck.message);
    return {
      target,
      success: false,
      error: 'Missing required dependencies. See error message above.'
    };
  }
  
  // Check if it's a TypeScript/Svelte file (for single file mode)
  if (fs.existsSync(target) && fs.statSync(target).isFile()) {
    if (!isTypeScriptOrSvelteFile(target)) {
      log('INFO', `Skipping non-TypeScript/Svelte file: ${target}`);
      return {
        target,
        skipped: true,
        reason: 'not a TypeScript/Svelte file'
      };
    }
    
    if (!fs.existsSync(target)) {
      log('WARNING', `File does not exist: ${target}`);
      return {
        target,
        skipped: true,
        reason: 'file does not exist'
      };
    }
  }
  
  log('INFO', `Running type and lint checks for: ${target}`);
  
  // Determine if we're checking a single file or the whole project
  const isSingleFile = fs.existsSync(target) && fs.statSync(target).isFile();
  
  // Run TypeScript checking
  let svelteCheckOutput = '';
  let svelteCheckExitCode = 0;
  
  try {
    if (isSingleFile && target.endsWith('.ts')) {
      // For single TypeScript files, use tsc directly (much faster)
      log('DEBUG', 'Using tsc for single TypeScript file');
      svelteCheckOutput = execSync(`pnpm exec tsc --noEmit --skipLibCheck "${target}"`, {
        encoding: 'utf8',
        stdio: ['pipe', 'pipe', 'pipe']
      });
    } else if (isSingleFile && target.endsWith('.svelte')) {
      // For single Svelte files, use svelte-check with file filter (faster than full check)
      log('DEBUG', 'Using svelte-check for single Svelte file');
      svelteCheckOutput = execSync(`pnpm exec svelte-check --output human-verbose --tsconfig ./tsconfig.json --threshold error --fail-on-warnings false`, {
        encoding: 'utf8',
        stdio: ['pipe', 'pipe', 'pipe'],
        cwd: path.dirname(target)
      });
    } else {
      // For directories or multiple files, run full svelte-check
      log('DEBUG', 'Using svelte-check for full project check');
      svelteCheckOutput = execSync('pnpm exec svelte-check --output human-verbose --tsconfig ./tsconfig.json', {
        encoding: 'utf8',
        stdio: ['pipe', 'pipe', 'pipe']
      });
    }
  } catch (error) {
    const err = error as NodeJS.ErrnoException & { status?: number; stdout?: string; stderr?: string };
    svelteCheckExitCode = err.status || 1;
    svelteCheckOutput = err.stdout || '';
    
    // If the command failed completely (not just type errors), check why
    if (!svelteCheckOutput && err.stderr) {
      const stderr = err.stderr.toString();
      if (stderr.includes('command not found') || stderr.includes('not recognized')) {
        console.error(`
❌ Failed to run svelte-check!

This usually means the dependencies aren't properly installed.
Try running: pnpm install

Error details: ${stderr}
`);
        return {
          target,
          success: false,
          error: 'Failed to run svelte-check. Dependencies may be missing.'
        };
      }
    }
  }
  
  log('DEBUG', `svelte-check exit code: ${svelteCheckExitCode}`);
  
  // Count type errors and warnings from svelte-check output
  const typeErrorCount = (svelteCheckOutput.match(/Error:/g) || []).length;
  const typeWarningCount = (svelteCheckOutput.match(/Warning:/g) || []).length;
  
  // Run ESLint for linting checks (only if it's a TS/JS/Svelte file)
  let eslintOutput = '';
  let eslintExitCode = 0;
  let eslintErrorCount = 0;
  let eslintWarningCount = 0;
  
  if (fs.existsSync(target) && fs.statSync(target).isFile() && isTypeScriptOrSvelteFile(target)) {
    try {
      // Run ESLint on the specific file with caching for speed
      eslintOutput = execSync(`pnpm exec eslint --cache --cache-location .eslintcache "${target}"`, {
        encoding: 'utf8',
        stdio: ['pipe', 'pipe', 'pipe']
      });
    } catch (error) {
      const err = error as NodeJS.ErrnoException & { status?: number; stdout?: string };
      eslintExitCode = err.status || 1;
      eslintOutput = err.stdout || '';
      
      // Parse ESLint output for error/warning counts
      const eslintLines = eslintOutput.split('\n');
      const summaryLine = eslintLines.find(line => line.includes('problem'));
      if (summaryLine) {
        const match = summaryLine.match(/✖\s+(\d+)\s+problems?\s+\((\d+)\s+errors?,\s+(\d+)\s+warnings?\)/);
        if (match) {
          eslintErrorCount = parseInt(match[2], 10);
          eslintWarningCount = parseInt(match[3], 10);
        }
      }
    }
    
    log('DEBUG', `eslint exit code: ${eslintExitCode}`);
    log('INFO', `ESLint found ${eslintErrorCount} errors and ${eslintWarningCount} warnings`);
  } else {
    log('INFO', `Skipping ESLint for ${target} (not a single file or not a JS/TS/Svelte file)`);
  }
  
  // Combine results
  const totalErrorCount = typeErrorCount + eslintErrorCount;
  const totalWarningCount = typeWarningCount + eslintWarningCount;
  
  log('INFO', `Total: ${totalErrorCount} errors and ${totalWarningCount} warnings`);
  
  if (svelteCheckExitCode === 0 && eslintExitCode === 0) {
    log('SUCCESS', `✅ All checks passed for ${target}`);
    return {
      target,
      success: true,
      svelte_check: {
        exit_code: svelteCheckExitCode,
        error_count: typeErrorCount,
        warning_count: typeWarningCount
      },
      eslint: {
        exit_code: eslintExitCode,
        error_count: eslintErrorCount,
        warning_count: eslintWarningCount
      }
    };
  } else {
    log('WARNING', `⚠️ Checks failed for ${target}`);
    
    // Process TypeScript errors if any
    let typeErrorLines = '';
    if (typeErrorCount > 0) {
      typeErrorLines = svelteCheckOutput.split('\n')
        .map((line, index, arr) => {
          if (line.startsWith('Error:')) {
            // Get context: 1 line before and 2 lines after
            const context = [];
            if (index > 0) context.push(arr[index - 1]);
            context.push(line);
            if (index < arr.length - 1) context.push(arr[index + 1]);
            if (index < arr.length - 2) context.push(arr[index + 2]);
            return context.join('\n');
          }
          return null;
        })
        .filter(Boolean)
        .slice(0, 5)
        .join('\n--\n');
    }
    
    // Process ESLint errors if any
    let eslintLines = '';
    if (eslintErrorCount > 0) {
      // Clean up ESLint output to show just the errors
      eslintLines = eslintOutput.split('\n')
        .filter(line => line.trim() && !line.startsWith('✖'))
        .slice(0, 10)
        .join('\n');
    }
    
    return {
      target,
      success: false,
      svelte_check: {
        exit_code: svelteCheckExitCode,
        error_count: typeErrorCount,
        warning_count: typeWarningCount,
        output: typeErrorCount > 0 ? typeErrorLines : undefined
      },
      eslint: {
        exit_code: eslintExitCode,
        error_count: eslintErrorCount,
        warning_count: eslintWarningCount,
        output: eslintErrorCount > 0 ? eslintLines : undefined
      }
    };
  }
}

function handleCliMode(targets: string[]): void {
  log('INFO', 'Running in CLI mode');
  
  let hasErrors = false;
  
  for (const target of targets) {
    const result = processTarget(target);
    console.log(JSON.stringify(result, null, 2));
    
    if (result.success === false) {
      hasErrors = true;
    }
  }
  
  if (hasErrors) {
    process.exit(1);
  }
}

function handleHookMode(): void {
  log('INFO', 'Running in hook mode (Claude Code PostToolUse)');
  
  let inputData = '';
  
  // Read from stdin
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', (chunk) => {
    inputData += chunk;
  });
  
  process.stdin.on('end', () => {
    if (!inputData) {
      log('WARNING', 'No input received from stdin');
      console.log(JSON.stringify({ error: 'No input received' }));
      process.exit(0);
    }
    
    log('DEBUG', `Received input: ${inputData.substring(0, 500)}...`);
    
    let hookInput: ClaudeHookInput;
    try {
      hookInput = JSON.parse(inputData);
    } catch (error) {
      log('ERROR', `Failed to parse JSON input: ${error}`);
      console.log(JSON.stringify({ error: 'Invalid JSON input' }));
      process.exit(1);
    }
    
    const toolName = hookInput.tool_name;
    log('DEBUG', `Parsed tool_name: ${toolName}`);
    
    // Only process Write, Edit, and MultiEdit tools
    if (toolName === 'Write' || toolName === 'Edit' || toolName === 'MultiEdit') {
      const filePath = hookInput.tool_input?.file_path;
      
      if (filePath) {
        log('INFO', `Processing ${toolName} operation on ${filePath}`);
        
        // Check if it's a TypeScript/Svelte file
        if (!isTypeScriptOrSvelteFile(filePath)) {
          log('DEBUG', `Skipping non-TypeScript/Svelte file: ${filePath}`);
          console.log(JSON.stringify({
            tool: toolName,
            target: filePath,
            skipped: true,
            reason: 'not a TypeScript/Svelte file'
          }));
          process.exit(0);
        }
        
        // Process the file
        const result = processTarget(filePath);
        
        // Check if we should block due to errors
        if (result.success === false) {
          log('ERROR', 'Blocking due to checking errors');
          
          const typeErrorCount = result.svelte_check?.error_count || 0;
          const eslintErrorCount = result.eslint?.error_count || 0;
          const totalErrors = typeErrorCount + eslintErrorCount;
          
          let errorMessage = 'The file has errors that must be fixed before continuing.\nPlease fix ALL the following issues:\n\n';
          
          if (typeErrorCount > 0) {
            const typeErrors = result.svelte_check?.output || '';
            errorMessage += `TypeScript Errors (${typeErrorCount}):\n${typeErrors}\n\n`;
          }
          
          if (eslintErrorCount > 0) {
            const eslintErrors = result.eslint?.output || '';
            errorMessage += `ESLint Errors (${eslintErrorCount}):\n${eslintErrors}\n\n`;
          }
          
          if (totalErrors === 0 && result.error) {
            // If there are no specific errors but the result failed, show the general error
            errorMessage = result.error;
          }
          
          const blockingResponse: HookResponse = {
            decision: 'block',
            reason: errorMessage + '\nFix these issues and try again.'
          };
          
          console.log(JSON.stringify(blockingResponse));
          
          // Also write errors to stderr for visibility
          console.error(`Checks failed with ${totalErrors} total errors`);
          
          // Exit with code 2 to ensure Claude sees the errors
          process.exit(2);
        } else {
          // Success or skipped - output normally
          console.log(JSON.stringify(result));
        }
      } else {
        log('WARNING', `No file_path found in ${toolName} input`);
        console.log(JSON.stringify({ error: 'No file_path found in tool input' }));
      }
    } else {
      log('DEBUG', `Ignoring tool: ${toolName}`);
      console.log(JSON.stringify({
        tool: toolName,
        skipped: true,
        reason: 'not a file editing tool'
      }));
    }
  });
}

// Main execution
function main(): void {
  log('INFO', '================================================================');
  log('INFO', 'TypeScript-on-save hook started');
  
  const args = process.argv.slice(2);
  
  if (args.length > 0) {
    // CLI mode - process command line arguments
    handleCliMode(args);
  } else if (process.stdin.isTTY) {
    // Interactive mode with no arguments - process current directory
    log('INFO', 'Running in CLI mode (no args, processing current directory)');
    const result = processTarget('.');
    console.log(JSON.stringify(result, null, 2));
    
    if (result.success === false) {
      process.exit(1);
    }
  } else {
    // Hook mode - read JSON from stdin
    handleHookMode();
  }
  
  log('INFO', 'TypeScript-on-save hook completed');
  log('INFO', '================================================================');
}

// Run the main function
main();