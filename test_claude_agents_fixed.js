#!/usr/bin/env node
/**
 * REAL FUNCTIONAL TEST: Claude Code Agents
 * Tests actual Claude Code CLI integration with agents
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Colors
const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  cyan: '\x1b[36m',
  reset: '\x1b[0m',
  bright: '\x1b[1m',
};

function colorPrint(color, text) {
  console.log(`${colors[color]}${text}${colors.reset}`);
}

function printHeader(text) {
  console.log('\n' + '='.repeat(70));
  colorPrint('cyan', `  ${text}`);
  console.log('='.repeat(70) + '\n');
}

async function loadAgentConfigs() {
  const agentsDir = '.claude/agents';
  const agents = {};

  // Load individual agent configs
  const agentFiles = [
    'claude-strategy-advisor.json',
    'claude-risk-advisor.json',
    'claude-funding-advisor.json',
    'claude-sentiment-analyzer.json',
  ];

  for (const file of agentFiles) {
    const filePath = path.join(agentsDir, file);
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, 'utf8');
      const config = JSON.parse(content);
      agents[config.name] = config;
      colorPrint('green', `Loaded: ${file}`);
    }
  }

  return agents;
}

async function runClaudeCode(task, agents) {
  return new Promise((resolve) => {
    const startTime = Date.now();

    // Convert agents object to JSON string
    const agentsJson = JSON.stringify(agents);

    colorPrint('yellow', `Testing: ${task.substring(0, 80)}...`);

    // Call Claude Code with agents JSON
    const proc = spawn('claude', ['--agents', agentsJson, '--print', task], {
      stdio: ['pipe', 'pipe', 'pipe'],
      shell: true,
    });

    let output = '';
    let error = '';

    proc.stdout.on('data', (data) => {
      const str = data.toString();
      output += str;
    });

    proc.stderr.on('data', (data) => {
      const str = data.toString();
      error += str;
      process.stderr.write(str);
    });

    proc.on('close', (code) => {
      const duration = Date.now() - startTime;
      resolve({
        success: code === 0,
        output,
        error,
        duration,
        code,
      });
    });

    proc.on('error', (err) => {
      resolve({
        success: false,
        output,
        error: err.message,
        duration: Date.now() - startTime,
        code: -1,
      });
    });
  });
}

async function main() {
  printHeader('REAL CLAUDE CODE AGENTS TEST');

  // Load agent configurations
  colorPrint('cyan', 'Loading agent configurations...\n');
  const agents = await loadAgentConfigs();

  if (Object.keys(agents).length === 0) {
    colorPrint('red', 'ERROR: No agent configurations found!');
    process.exit(1);
  }

  colorPrint('green', `\nLoaded ${Object.keys(agents).length} agents\n`);

  const tests = [
    {
      name: 'Strategy Analysis',
      task: 'Analyze BTC-USD trading opportunity. Current price: $50,000. Should I buy, sell, or hold?',
    },
    {
      name: 'Risk Assessment',
      task: 'Assess risk for a $10,000 BTC position with 5x leverage. What is the maximum drawdown risk?',
    },
  ];

  let passed = 0;
  let failed = 0;

  for (const test of tests) {
    printHeader(`TEST: ${test.name}`);

    try {
      const result = await runClaudeCode(test.task, agents);

      // Show output summary
      if (result.output) {
        const lines = result.output.split('\n').slice(0, 5);
        console.log('Output preview:');
        lines.forEach((line) => console.log('  ' + line));
      }

      if (result.success) {
        colorPrint('green', `\n[PASSED] ${test.name} (${result.duration}ms)`);
        passed++;
      } else {
        colorPrint(
          'red',
          `\n[FAILED] ${test.name} - Exit code: ${result.code}`
        );
        if (result.error) {
          colorPrint('red', `Error: ${result.error.substring(0, 200)}`);
        }
        failed++;
      }
    } catch (error) {
      colorPrint('red', `\n[ERROR] ${test.name}: ${error.message}`);
      failed++;
    }

    console.log('\n' + '-'.repeat(70) + '\n');

    // Wait between tests
    await new Promise((resolve) => setTimeout(resolve, 2000));
  }

  // Summary
  printHeader('TEST SUMMARY');

  console.log(`Total tests: ${tests.length}`);
  colorPrint('green', `Passed: ${passed}`);
  colorPrint(failed > 0 ? 'red' : 'green', `Failed: ${failed}`);

  const successRate = ((passed / tests.length) * 100).toFixed(1);
  console.log(`Success rate: ${successRate}%`);

  if (failed === 0) {
    colorPrint(
      'green',
      '\nALL TESTS PASSED - Claude Code integration working!\n'
    );
    process.exit(0);
  } else {
    colorPrint('red', '\nSOME TESTS FAILED\n');
    process.exit(1);
  }
}

main().catch((error) => {
  colorPrint('red', `Fatal error: ${error.message}`);
  console.error(error);
  process.exit(1);
});
