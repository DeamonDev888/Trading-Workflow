#!/usr/bin/env node
/**
 * 🧪 Claude Code Agents Test - Integration Test
 * Tests the real Claude Code agents integration
 */

import { spawn, ChildProcess } from 'child_process';
import fs from 'fs';
import path from 'path';

interface TestResult {
  test: string;
  passed: boolean;
  duration: number;
  error?: string;
  output?: string;
}

interface Colors {
  green: string;
  red: string;
  yellow: string;
  cyan: string;
  reset: string;
  bright: string;
}

const colors: Colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  cyan: '\x1b[36m',
  reset: '\x1b[0m',
  bright: '\x1b[1m',
};

function colorPrint(color: keyof Colors, text: string): void {
  console.log(`${colors[color]}${text}${colors.reset}`);
}

async function runPythonScript(
  scriptPath: string,
  args: string[] = []
): Promise<{ success: boolean; output: string; error?: string }> {
  return new Promise((resolve) => {
    const startTime = Date.now();

    const proc = spawn('python', [scriptPath, ...args], {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: process.cwd(),
    });

    let output = '';
    let error = '';

    proc.stdout?.on('data', (data: Buffer) => {
      const str = data.toString();
      output += str;
      if (process.stdout.writable) {
        process.stdout.write(str);
      }
    });

    proc.stderr?.on('data', (data: Buffer) => {
      const str = data.toString();
      error += str;
      if (process.stderr.writable) {
        process.stderr.write(str);
      }
    });

    proc.on('close', (code: number | null) => {
      const duration = Date.now() - startTime;
      const success = code === 0;
      resolve({ success, output, error: error || undefined });
    });

    proc.on('error', (err: Error) => {
      const duration = Date.now() - startTime;
      resolve({ success: false, output, error: err.message });
    });
  });
}

async function testOrchestratorIntegration(): Promise<TestResult> {
  const startTime = Date.now();
  colorPrint(
    'cyan',
    '\n[TEST] Testing Claude Code Orchestrator Integration...'
  );

  try {
    // Test 1: Import and initialize
    colorPrint('yellow', '  [1/4] Testing orchestrator initialization...');
    const initResult = await runPythonScript(
      'scripts/test_claude_code_integration.py',
      ['--quick']
    );

    if (!initResult.success) {
      return {
        test: 'orchestrator_integration',
        passed: false,
        duration: Date.now() - startTime,
        error: 'Failed to initialize orchestrator',
        output: initResult.output,
      };
    }

    // Test 2: Run single agent test
    colorPrint('yellow', '  [2/4] Testing single agent execution...');
    const singleResult = await runPythonScript(
      'scripts/claude_code_agent_runner.py',
      [
        '--mode',
        'single',
        '--agent',
        'claude-strategy-advisor',
        '--task',
        'Test BTC signal',
        '--iterations',
        '1',
        '--no-save',
      ]
    );

    if (!singleResult.success) {
      return {
        test: 'single_agent',
        passed: false,
        duration: Date.now() - startTime,
        error: 'Failed to execute single agent',
        output: singleResult.output,
      };
    }

    // Test 3: Run complete analysis
    colorPrint('yellow', '  [3/4] Testing complete analysis...');
    const completeResult = await runPythonScript(
      'scripts/claude_code_agent_runner.py',
      ['--mode', 'complete', '--no-save']
    );

    if (!completeResult.success) {
      return {
        test: 'complete_analysis',
        passed: false,
        duration: Date.now() - startTime,
        error: 'Failed to run complete analysis',
        output: completeResult.output,
      };
    }

    // Test 4: Verify system reliability
    colorPrint('yellow', '  [4/4] Verifying system reliability...');
    const reliabilityResult = await runPythonScript(
      'scripts/test_claude_code_integration.py',
      ['--reliability-check']
    );

    if (!reliabilityResult.success) {
      return {
        test: 'reliability_check',
        passed: false,
        duration: Date.now() - startTime,
        error: 'System reliability check failed',
        output: reliabilityResult.output,
      };
    }

    return {
      test: 'orchestrator_integration',
      passed: true,
      duration: Date.now() - startTime,
      output: 'All tests passed',
    };
  } catch (error: any) {
    return {
      test: 'orchestrator_integration',
      passed: false,
      duration: Date.now() - startTime,
      error: error.message,
    };
  }
}

async function testAgentCommunication(): Promise<TestResult> {
  const startTime = Date.now();
  colorPrint('cyan', '\n[TEST] Testing Agent Communication...');

  try {
    // Test direct agent call
    const result = await runPythonScript(
      'scripts/claude_code_agent_runner.py',
      [
        '--mode',
        'delegation',
        '--task',
        'Quick health check of trading system',
        '--no-save',
      ]
    );

    const passed = result.success && result.output.includes('success');

    return {
      test: 'agent_communication',
      passed,
      duration: Date.now() - startTime,
      output: result.output,
    };
  } catch (error: any) {
    return {
      test: 'agent_communication',
      passed: false,
      duration: Date.now() - startTime,
      error: error.message,
    };
  }
}

async function testDataAggregation(): Promise<TestResult> {
  const startTime = Date.now();
  colorPrint('cyan', '\n[TEST] Testing Data Aggregation...');

  try {
    // Create test context
    const testContext = {
      symbol: 'BTC-USD',
      price: 50000,
      volume: 1000000,
      timestamp: new Date().toISOString(),
    };

    // Write context file
    const contextPath = 'test_context.json';
    fs.writeFileSync(contextPath, JSON.stringify(testContext, null, 2));

    // Run aggregation test
    const result = await runPythonScript(
      'scripts/claude_code_agent_runner.py',
      [
        '--mode',
        'single',
        '--agent',
        'claude-risk-advisor',
        '--task',
        'Assess risk for BTC position',
        '--context',
        contextPath,
        '--iterations',
        '2',
        '--no-save',
      ]
    );

    // Cleanup
    if (fs.existsSync(contextPath)) {
      fs.unlinkSync(contextPath);
    }

    const passed = result.success && result.output.includes('confidence');

    return {
      test: 'data_aggregation',
      passed,
      duration: Date.now() - startTime,
      output: result.output,
    };
  } catch (error: any) {
    return {
      test: 'data_aggregation',
      passed: false,
      duration: Date.now() - startTime,
      error: error.message,
    };
  }
}

async function testReliabilityMonitoring(): Promise<TestResult> {
  const startTime = Date.now();
  colorPrint('cyan', '\n[TEST] Testing Reliability Monitoring...');

  try {
    // Run reliability demo
    const result = await runPythonScript(
      'scripts/claude_code_reliability_demo.py'
    );

    const passed =
      result.success &&
      result.output.includes('reliability') &&
      result.output.includes('passed');

    return {
      test: 'reliability_monitoring',
      passed,
      duration: Date.now() - startTime,
      output: result.output,
    };
  } catch (error: any) {
    return {
      test: 'reliability_monitoring',
      passed: false,
      duration: Date.now() - startTime,
      error: error.message,
    };
  }
}

async function checkPrerequisites(): Promise<{
  ok: boolean;
  missing: string[];
}> {
  colorPrint('cyan', '\n[SETUP] Checking prerequisites...');

  const missing: string[] = [];

  // Check Python
  try {
    spawn('python', ['--version'], { stdio: 'ignore' });
    colorPrint('green', '  ✅ Python found');
  } catch {
    missing.push('Python');
    colorPrint('red', '  ❌ Python not found');
  }

  // Check Claude Code agents
  const agentFiles = [
    '.claude/agents/claude-strategy-advisor.json',
    '.claude/agents/claude-risk-advisor.json',
    '.claude/agents/claude-funding-advisor.json',
    '.claude/agents/claude-sentiment-analyzer.json',
  ];

  for (const file of agentFiles) {
    if (fs.existsSync(file)) {
      colorPrint('green', `  ✅ ${path.basename(file)}`);
    } else {
      missing.push(file);
      colorPrint('red', `  ❌ ${file} missing`);
    }
  }

  // Check orchestrator
  if (fs.existsSync('src/agents/claude_code_orchestrator.py')) {
    colorPrint('green', '  ✅ Orchestrator found');
  } else {
    missing.push('src/agents/claude_code_orchestrator.py');
    colorPrint('red', '  ❌ Orchestrator missing');
  }

  return { ok: missing.length === 0, missing };
}

async function main(): Promise<void> {
  console.log('\n' + '='.repeat(80));
  colorPrint('bright', '🧪 NOVAQUOTE CLAUDE CODE AGENTS - REAL SYSTEM TEST');
  console.log('='.repeat(80));

  // Check prerequisites
  const { ok, missing } = await checkPrerequisites();

  if (!ok) {
    colorPrint('red', '\n❌ Missing prerequisites:');
    missing.forEach((item) => console.log(`  - ${item}`));
    console.log('\nPlease install missing components before running tests.\n');
    process.exit(1);
  }

  // Run tests
  const tests: (() => Promise<TestResult>)[] = [
    testOrchestratorIntegration,
    testAgentCommunication,
    testDataAggregation,
    testReliabilityMonitoring,
  ];

  const results: TestResult[] = [];
  let passed = 0;
  let failed = 0;

  for (const testFunc of tests) {
    try {
      const result = await testFunc();
      results.push(result);

      if (result.passed) {
        passed++;
        colorPrint(
          'green',
          `\n✅ Test passed: ${result.test} (${result.duration}ms)`
        );
      } else {
        failed++;
        colorPrint('red', `\n❌ Test failed: ${result.test}`);
        if (result.error) {
          colorPrint('red', `   Error: ${result.error}`);
        }
      }
    } catch (error: any) {
      failed++;
      colorPrint('red', `\n❌ Test crashed: ${testFunc.name}`);
      colorPrint('red', `   Error: ${error.message}`);
    }
  }

  // Summary
  console.log('\n' + '='.repeat(80));
  colorPrint('bright', '📊 TEST SUMMARY');
  console.log('='.repeat(80));

  console.log(`\nTotal tests: ${results.length}`);
  colorPrint('green', `Passed: ${passed}`);
  colorPrint(failed > 0 ? 'red' : 'green', `Failed: ${failed}`);

  const successRate = ((passed / results.length) * 100).toFixed(1);
  console.log(`Success rate: ${successRate}%`);

  if (failed === 0) {
    colorPrint(
      'green',
      '\n🎉 ALL TESTS PASSED - Claude Code Integration is working!'
    );
    console.log('\nThe system is ready for production use.\n');
    process.exit(0);
  } else {
    colorPrint('red', '\n⚠️  SOME TESTS FAILED');
    console.log('\nPlease review the errors above and fix the issues.\n');
    process.exit(1);
  }
}

// Handle errors
process.on('uncaughtException', (error: Error) => {
  colorPrint('red', `\n💥 Uncaught Exception: ${error.message}`);
  console.error(error.stack);
  process.exit(1);
});

process.on('unhandledRejection', (reason: any, promise: Promise<any>) => {
  colorPrint('red', `\n💥 Unhandled Rejection: ${reason}`);
  console.error('Promise:', promise);
  process.exit(1);
});

// Run tests
main();
