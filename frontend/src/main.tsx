import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { AppInitializer } from './components/common/AppInitializer';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { initSentry } from './config/sentry';
import { SENTRY_DSN, SENTRY_ENVIRONMENT, SENTRY_ENABLED } from './config/env';
import '@fontsource/inter/300.css';
import '@fontsource/inter/400.css';
import '@fontsource/inter/500.css';
import '@fontsource/inter/600.css';
import '@fontsource/inter/700.css';
import '@fontsource/inter/800.css';
import './style.css';

// Initialize Sentry (non-blocking)
let sentryInitialized = false;
try {
  initSentry(SENTRY_DSN, SENTRY_ENVIRONMENT, SENTRY_ENABLED);
  sentryInitialized = true;
} catch (_error) {
  // Don't block app initialization if Sentry fails
}

// Create QueryClient with error handling and global configuration
let queryClient: QueryClient;
try {
  queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        refetchOnWindowFocus: false,
        retry: 1,
        staleTime: 2 * 60 * 1000, // 2 minutes - data is considered fresh for 2 minutes
        gcTime: 5 * 60 * 1000, // 5 minutes - cache garbage collection time (formerly cacheTime)
      },
      mutations: {
        retry: 0, // Don't retry mutations by default
        onError: (error) => {
          // Global mutation error handler
          // Individual mutations can still override this with their own onError
          console.error('Mutation error:', error);
        },
      },
    },
  });
} catch (_error) {
  // Fallback to basic QueryClient
  queryClient = new QueryClient();
}

// Render app with proper error handling
const rootElement = document.getElementById('root');
if (!rootElement) {
  // Show error UI directly in HTML if root element is missing
  document.body.innerHTML = `
    <div style="padding: 40px; text-align: center; font-family: system-ui, sans-serif;">
      <h1 style="color: #dc2626; font-size: 24px; margin-bottom: 16px;">Application Error</h1>
      <p style="color: #666; font-size: 16px; margin-bottom: 8px;">Root element not found</p>
      <p style="color: #999; font-size: 14px;">Please ensure the HTML includes a &lt;div id="root"&gt;&lt;/div&gt; element.</p>
    </div>
  `;
  throw new Error('Root element not found');
}

// Render function with comprehensive error handling
const renderApp = () => {
  try {
    const root = ReactDOM.createRoot(rootElement);
    
    root.render(
      <React.StrictMode>
        <ErrorBoundary>
          <QueryClientProvider client={queryClient}>
            <BrowserRouter>
              <AppInitializer
                onInitializationError={(error) => {
                  // Report initialization errors to Sentry if available
                  if (sentryInitialized) {
                    try {
                      // Dynamic import to avoid issues if Sentry isn't loaded
                      import('@sentry/react').then((Sentry) => {
                        Sentry.captureException(error, {
                          tags: { component: 'AppInitializer' },
                          level: 'error',
                        });
                      }).catch(() => {
                        // Sentry not available, ignore
                      });
                    } catch (_sentryError) {
                      // Failed to report error to Sentry, ignore
                    }
                  }
                }}
              >
                <App />
              </AppInitializer>
            </BrowserRouter>
          </QueryClientProvider>
        </ErrorBoundary>
      </React.StrictMode>
    );
  } catch (error) {
    
    // Show user-friendly error UI
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    const errorStack = error instanceof Error ? error.stack : undefined;
    
    rootElement.innerHTML = `
      <div style="padding: 40px; text-align: center; font-family: system-ui, sans-serif; background: #f9fafb; min-height: 100vh; display: flex; align-items: center; justify-content: center;">
        <div style="max-width: 500px; background: white; border-radius: 8px; padding: 32px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
          <div style="margin-bottom: 24px;">
            <div style="width: 48px; height: 48px; margin: 0 auto; background: #fee2e2; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
              <svg style="width: 24px; height: 24px; color: #dc2626;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
          </div>
          <h1 style="color: #111827; font-size: 24px; font-weight: 600; margin-bottom: 12px;">Application Error</h1>
          <p style="color: #6b7280; font-size: 16px; margin-bottom: 24px;">Failed to initialize the application.</p>
          <div style="background: #f3f4f6; border-radius: 6px; padding: 12px; margin-bottom: 24px; text-align: left;">
            <p style="color: #374151; font-size: 14px; font-family: monospace; word-break: break-word; margin: 0;">${errorMessage}</p>
          </div>
          <div style="display: flex; gap: 12px; justify-content: center;">
            <button 
              onclick="window.location.reload()" 
              style="background: #ea580c; color: white; border: none; border-radius: 6px; padding: 10px 20px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s;"
              onmouseover="this.style.background='#c2410c'"
              onmouseout="this.style.background='#ea580c'"
            >
              Reload Page
            </button>
            ${errorStack ? `
              <button 
                onclick="alert('Error details:\\n\\n${errorStack.replace(/'/g, "\\'")}')" 
                style="background: white; color: #374151; border: 1px solid #d1d5db; border-radius: 6px; padding: 10px 20px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s;"
                onmouseover="this.style.background='#f9fafb'"
                onmouseout="this.style.background='white'"
              >
                Show Details
              </button>
            ` : ''}
          </div>
        </div>
      </div>
    `;
  }
};

// Execute render
renderApp();

