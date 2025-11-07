module.exports = [
  {
    files: ['**/*.{js,ts}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
    },
    plugins: {
      '@typescript-eslint': require('@typescript-eslint/eslint-plugin'),
    },
    languageOptions: {
      parser: require('@typescript-eslint/parser'),
    },
    rules: {
      'no-var': 'error',
      'prefer-const': 'error',
      '@typescript-eslint/no-unused-vars': 'warn',
    },
  },
];
