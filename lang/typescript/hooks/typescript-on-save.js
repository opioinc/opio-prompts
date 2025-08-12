#!/usr/bin/env node
// ABOUTME: TypeScript/Svelte hook for Claude Code that runs pnpm check (svelte-check) on saved files
// ABOUTME: Blocks further operations if type checking fails, ensuring LLM changes are compliant
import { execSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
// Get __dirname equivalent in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
// Logging setup
const SCRIPT_DIR = __dirname;
const LOG_DIR = path.join(SCRIPT_DIR, 'logs');
const LOG_FILE = path.join(LOG_DIR, `typescript-on-save-${new Date().toISOString().split('T')[0]}.log`);
// Ensure log directory exists
if (!fs.existsSync(LOG_DIR)) {
    fs.mkdirSync(LOG_DIR, { recursive: true });
}
function log(level, message) {
    const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
    const logMessage = `${timestamp} | ${level} | ${message}\n`;
    fs.appendFileSync(LOG_FILE, logMessage);
}
function isTypeScriptOrSvelteFile(filePath) {
    return /\.(ts|tsx|js|jsx|svelte)$/.test(filePath);
}
function processTarget(target) {
    log('INFO', `Processing target: ${target}`);
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
    log('INFO', `Running pnpm check for: ${target}`);
    // Run svelte-check with machine output for parsing
    let machineOutput = '';
    let humanOutput = '';
    let exitCode = 0;
    try {
        machineOutput = execSync('npx svelte-check --output machine --tsconfig ./tsconfig.json', {
            encoding: 'utf8',
            stdio: ['pipe', 'pipe', 'pipe']
        });
    }
    catch (error) {
        exitCode = error.status || 1;
        machineOutput = error.stdout || '';
    }
    // Also get human-readable output for error messages
    try {
        humanOutput = execSync('npx svelte-check --output human-verbose --tsconfig ./tsconfig.json', {
            encoding: 'utf8',
            stdio: ['pipe', 'pipe', 'pipe']
        });
    }
    catch (error) {
        humanOutput = error.stdout || '';
    }
    log('DEBUG', `pnpm check exit code: ${exitCode}`);
    // Count errors and warnings from machine output
    const errorCount = (machineOutput.match(/ ERROR /g) || []).length;
    const warningCount = (machineOutput.match(/ WARNING /g) || []).length;
    log('INFO', `Type checking found ${errorCount} errors and ${warningCount} warnings`);
    if (exitCode === 0) {
        log('SUCCESS', `✅ All checks passed for ${target}`);
        return {
            target,
            success: true,
            svelte_check: {
                exit_code: exitCode,
                error_count: errorCount,
                warning_count: warningCount
            }
        };
    }
    else {
        log('WARNING', `⚠️ Type checking failed for ${target}`);
        // Extract error lines from human-readable output
        const errorLines = humanOutput.split('\n')
            .map((line, index, arr) => {
            if (line.startsWith('Error:')) {
                // Get context: 1 line before and 2 lines after
                const context = [];
                if (index > 0)
                    context.push(arr[index - 1]);
                context.push(line);
                if (index < arr.length - 1)
                    context.push(arr[index + 1]);
                if (index < arr.length - 2)
                    context.push(arr[index + 2]);
                return context.join('\\n');
            }
            return null;
        })
            .filter(Boolean)
            .slice(0, 10)
            .join('\\n--\\n');
        return {
            target,
            success: false,
            svelte_check: {
                exit_code: exitCode,
                error_count: errorCount,
                warning_count: warningCount,
                output: errorLines
            }
        };
    }
}
function handleCliMode(targets) {
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
function handleHookMode() {
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
        let hookInput;
        try {
            hookInput = JSON.parse(inputData);
        }
        catch (error) {
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
                    log('ERROR', 'Blocking due to type checking errors');
                    const errorCount = result.svelte_check?.error_count || 0;
                    const errorOutput = result.svelte_check?.output || '';
                    const blockingResponse = {
                        decision: 'block',
                        reason: `The file has type checking errors that must be fixed before continuing.\nPlease fix ALL the following issues (even if they existed before your changes):\n\nType checking found ${errorCount} errors:\n${errorOutput}\n\nFix these issues and try again.`
                    };
                    console.log(JSON.stringify(blockingResponse));
                    // Also write errors to stderr for visibility
                    console.error(`Type checking failed with ${errorCount} errors`);
                    // Exit with code 2 to ensure Claude sees the errors
                    process.exit(2);
                }
                else {
                    // Success or skipped - output normally
                    console.log(JSON.stringify(result));
                }
            }
            else {
                log('WARNING', `No file_path found in ${toolName} input`);
                console.log(JSON.stringify({ error: 'No file_path found in tool input' }));
            }
        }
        else {
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
function main() {
    log('INFO', '================================================================');
    log('INFO', 'TypeScript-on-save hook started');
    const args = process.argv.slice(2);
    if (args.length > 0) {
        // CLI mode - process command line arguments
        handleCliMode(args);
    }
    else if (process.stdin.isTTY) {
        // Interactive mode with no arguments - process current directory
        log('INFO', 'Running in CLI mode (no args, processing current directory)');
        const result = processTarget('.');
        console.log(JSON.stringify(result, null, 2));
        if (result.success === false) {
            process.exit(1);
        }
    }
    else {
        // Hook mode - read JSON from stdin
        handleHookMode();
    }
    log('INFO', 'TypeScript-on-save hook completed');
    log('INFO', '================================================================');
}
// Run the main function
main();
