import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { sentryVitePlugin } from '@sentry/vite-plugin';
import { visualizer } from 'rollup-plugin-visualizer';
import path from 'path';

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    // Sentry plugin for source maps upload (only in production builds)
    process.env.NODE_ENV === 'production' && process.env.SENTRY_AUTH_TOKEN
      ? sentryVitePlugin({
          org: process.env.SENTRY_ORG,
          project: process.env.SENTRY_PROJECT,
          authToken: process.env.SENTRY_AUTH_TOKEN,
          sourcemaps: {
            assets: './dist/**',
            ignore: ['node_modules'],
            rewriteSources: (source) => {
              // Remove webpack:// prefix and normalize paths
              return source.replace(/^webpack:\/\//, '');
            },
          },
        })
      : null,
    // Bundle visualizer (run with ANALYZE=true npm run build)
    process.env.ANALYZE === 'true'
      ? visualizer({
          open: true,
          filename: 'dist/stats.html',
          gzipSize: true,
          brotliSize: true,
        })
      : null,
  ].filter(Boolean),
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    // Generate source maps for Sentry (only in production)
    sourcemap: process.env.NODE_ENV === 'production',
    // Code splitting configuration
    rollupOptions: {
      output: {
        // Manual chunk splitting for better caching
        manualChunks: (id) => {
          // Vendor chunks
          if (id.includes('node_modules')) {
            // React and React DOM
            if (id.includes('react') || id.includes('react-dom')) {
              return 'vendor-react';
            }
            // React Router
            if (id.includes('react-router')) {
              return 'vendor-router';
            }
            // React Query
            if (id.includes('@tanstack/react-query')) {
              return 'vendor-query';
            }
            // Leaflet (large library - separate chunk)
            if (id.includes('leaflet')) {
              return 'vendor-leaflet';
            }
            // Other node_modules
            return 'vendor';
          }
        },
        // Chunk file naming
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]',
      },
    },
    // Chunk size warnings
    chunkSizeWarningLimit: 1000, // 1MB
  },
});

