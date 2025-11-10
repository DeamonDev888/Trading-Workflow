#!/usr/bin/env node
/**
 * SIMPLE TEST: Claude Code with single agent
 * Tests Claude Code CLI with one agent at a time
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
};

function colorPrint(color, text) {
  console.log(`${colors[color]}${text}${colors.reset}`);
}

async function runSingleAgent(agentName, task) {
  return new Promise((resolve) => {
    const startTime = Date.now();

    colorPrint('yellow', `Testing ${agentName}...`);

    const proc = spawn('claude', ['--print', task], {
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
  });
}

async function main() {
  console.log('\n' + '='.repeat(70));
  colorPrint('cyan', '  CLAUDE CODE BASIC FUNCTIONALITY TEST');
  console.log('='.repeat(70) + '\n');

  const tests = [
    {
      name: 'Strategy Query',
      task: 'As a trading strategy expert, analyze this scenario: BTC is at $50,000. The RSI is oversold at 25, MACD is bullish, and volume is increasing. What is your recommendation: BUY, SELL, or HOLD? Provide reasoning.',
    },
    {
      name: 'Risk Analysis',
      task: 'As a risk management expert, assess this position: Long 1 BTC at $50,000 with 5x leverage. Current P&L is -$1,000. What is the recommended action and stop-loss level?',
    },
  ];

  let passed = 0;
  let failed = 0;

  for (const test of tests) {
    console.log(`\nTest: ${test.name}`);
    console.log('-'.repeat(70));

    try {
      const result = await runSingleAgent('claude', test.task);

      if (result.success && result.output.length > 100) {
        colorPrint('green', `[PASSED] ${test.name} (${result.duration}ms)`);
        passed++;
        // Show first 300 chars of output
        console.log('Preview:', result.output.substring(0, 300) + '...');
      } else {
        colorPrint('red', `[FAILED] ${test.name}`);
        if (result.error) {
          console.log('Error:', result.error.substring(0, 200));
        }
        failed++;
      }
    } catch (error) {
      colorPrint('red', `[ERROR] ${test.name}: ${error.message}`);
      failed++;
    }
  }

  console.log('\n' + '='.repeat(70));
  console.log(`Total: ${tests.length} | Passed: ${passed} | Failed: ${failed}`);
  console.log('='.repeat(70) + '\n');

  if (failed === 0) {
    colorPrint('green', 'SUCCESS: Claude Code is working correctly!\n');
  } else {
    colorPrint('red', 'Some tests failed\n');
  }
}

main();
