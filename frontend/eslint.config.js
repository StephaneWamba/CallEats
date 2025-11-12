import js from '@eslint/js';
import tseslint from '@typescript-eslint/eslint-plugin';
import tsparser from '@typescript-eslint/parser';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import complexity from 'eslint-plugin-complexity';

export default [
  {
    files: ['**/*.{js,jsx,ts,tsx}'],
    languageOptions: {
      parser: tsparser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        ecmaFeatures: {
          jsx: true,
        },
      },
      globals: {
        window: 'readonly',
        document: 'readonly',
        console: 'readonly',
        localStorage: 'readonly',
        sessionStorage: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        setInterval: 'readonly',
        clearInterval: 'readonly',
        fetch: 'readonly',
        alert: 'readonly',
        File: 'readonly',
        FileReader: 'readonly',
        FormData: 'readonly',
        HTMLInputElement: 'readonly',
        HTMLButtonElement: 'readonly',
        HTMLDivElement: 'readonly',
        HTMLImageElement: 'readonly',
        IntersectionObserver: 'readonly',
        React: 'readonly',
        L: 'readonly', // Leaflet
      },
    },
    plugins: {
      '@typescript-eslint': tseslint,
      react,
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
      complexity,
    },
    rules: {
      ...js.configs.recommended.rules,
      ...react.configs.recommended.rules,
      ...react.configs['jsx-runtime'].rules,
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],
      '@typescript-eslint/no-unused-vars': [
        'warn',
        {
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_',
          caughtErrorsIgnorePattern: '^_',
        },
      ],
      'no-unused-vars': 'off', // Use TypeScript version instead
      'react/prop-types': 'off', // Using TypeScript for prop validation
      'no-console': 'off', // We removed console logs already
      'react/no-unescaped-entities': 'warn', // Allow quotes/apostrophes in JSX
      'no-useless-catch': 'warn', // Allow re-throwing for error handling
      'react-hooks/exhaustive-deps': 'warn', // Warn about missing dependencies
      'react-hooks/set-state-in-effect': 'warn', // Warn about setState in effects
      'react-hooks/rules-of-hooks': 'error', // Error on hook violations
      'react-refresh/only-export-components': 'warn', // Warn about fast refresh
      'react-hooks/purity': 'warn', // Warn about accessing refs during render (false positives with state)
      'react-hooks/refs': 'warn', // Warn about accessing refs during render (false positives - isVisible is state, not ref)
      // Complexity rules
      'complexity': ['warn', { max: 15 }], // Warn on high cyclomatic complexity
      'max-depth': ['warn', { max: 4 }], // Warn on deeply nested code
      'max-lines-per-function': ['warn', { max: 100, skipBlankLines: true, skipComments: true }], // Warn on long functions
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
  },
  {
    ignores: [
      'dist',
      'node_modules',
      '*.config.js',
      '*.config.ts',
      'test-react-app/**',
      'vite.config.ts',
      'tailwind.config.js',
      'postcss.config.js',
    ],
  },
];

