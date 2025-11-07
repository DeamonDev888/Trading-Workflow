/**
 * 🧪 Lanceur de Tests NOVAQUOTE
 * Exécute tous les tests disponibles dans le projet
 */

const { execSync } = require('child_process');
const path = require('path');

console.log('🚀 NOVAQUOTE Trading System - Test Suite Runner');
console.log('='.repeat(60));

const tests = [
  {
    name: 'System Health Tests',
    file: 'test-system.js',
    description: 'Test des serveurs backend/frontend et API',
  },
  {
    name: 'Structured Logging Tests',
    file: 'test-structured-logger.js',
    description: 'Test du système de logging structuré',
  },
];

async function runTest(test) {
  return new Promise((resolve) => {
    console.log(`\n🔍 Running ${test.name}...`);
    console.log(`📝 ${test.description}`);
    console.log('-'.repeat(40));

    try {
      const output = execSync(`node "${test.file}"`, {
        cwd: __dirname,
        encoding: 'utf8',
        timeout: 30000,
      });

      console.log(output);
      console.log('✅ Test completed successfully');
      resolve({ success: true, output });
    } catch (error) {
      console.error('❌ Test failed:');
      console.error(error.stdout || error.message);
      resolve({ success: false, error: error.message });
    }
  });
}

async function main() {
  const results = [];

  for (const test of tests) {
    const result = await runTest(test);
    results.push({ ...test, ...result });
  }

  console.log('\n' + '='.repeat(60));
  console.log('📊 TEST RESULTS SUMMARY');
  console.log('='.repeat(60));

  const passed = results.filter((r) => r.success).length;
  const total = results.length;

  results.forEach((result) => {
    const status = result.success ? '✅ PASS' : '❌ FAIL';
    console.log(`${status} ${result.name}`);
  });

  console.log('-'.repeat(60));
  console.log(`Total: ${passed}/${total} tests passed`);

  if (passed === total) {
    console.log('🎉 ALL TESTS PASSED!');
    console.log('✅ System is ready for production');
    process.exit(0);
  } else {
    console.log('⚠️ SOME TESTS FAILED');
    console.log('❌ Please fix the issues before deploying');
    process.exit(1);
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { runTest, main };
