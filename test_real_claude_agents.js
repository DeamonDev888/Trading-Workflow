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

async function runClaudeCode(task, agentConfig) {
  return new Promise((resolve) => {
    const startTime = Date.now();

    colorPrint('yellow', `Testing: ${task}`);

    // Call Claude Code with agents
    const proc = spawn('claude', ['--agents', agentConfig, task], {
      stdio: ['pipe', 'pipe', 'pipe'],
      shell: true,
    });

    let output = '';
    let error = '';

    proc.stdout.on('data', (data) => {
      const str = data.toString();
      output += str;
      process.stdout.write(str);
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

  // Check if agents exist
  const agentConfig = '@.claude/agents/claude-agents.json';
  if (!fs.existsSync('.claude/agents/claude-agents.json')) {
    colorPrint('red', 'ERROR: .claude/agents/claude-agents.json not found!');
    process.exit(1);
  }

  colorPrint('green', 'Found: .claude/agents/claude-agents.json');
  colorPrint('green', 'Found: 4 agent config files\n');

  const tests = [
    {
      name: 'Strategy Analysis',
      task: 'Analyze BTC-USD trading opportunity. Current price: $50,000. Should I buy, sell, or hold? Provide technical analysis with entry/exit points.',
    },
    {
      name: 'Risk Assessment',
      task: 'Assess risk for a $10,000 BTC position with 5x leverage. What is the maximum drawdown risk and recommended stop-loss?',
    },
    {
      name: 'Funding Analysis',
      task: 'Analyze funding rates for ETH-USD perpetual. Current rate: 0.01%. Should I long or short based on funding arbitrage?',
    },
    {
      name: 'Sentiment Analysis',
      task: 'Analyze current crypto market sentiment. Based on news and social media, is sentiment bullish or bearish for Bitcoin?',
    },
  ];

  let passed = 0;
  let failed = 0;

  for (const test of tests) {
    printHeader(`TEST: ${test.name}`);

    try {
      const result = await runClaudeCode(test.task, agentConfig);

      if (result.success) {
        colorPrint('green', `\n[PASSED] ${test.name} (${result.duration}ms)`);
        passed++;
      } else {
        colorPrint(
          'red',
          `\n[FAILED] ${test.name} - Exit code: ${result.code}`
        );
        if (result.error) {
          colorPrint('red', `Error: ${result.error}`);
        }
        failed++;
      }
    } catch (error) {
      colorPrint('red', `\n[ERROR] ${test.name}: ${error.message}`);
      failed++;
    }

    console.log('\n' + '-'.repeat(70) + '\n');
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
