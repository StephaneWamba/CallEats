import * as Sentry from '@sentry/react';

/**
 * Initialize Sentry for error tracking and monitoring
 * 
 * This should be called once at app startup, before rendering the app.
 * 
 * @param dsn - Sentry DSN (Data Source Name) from your Sentry project settings
 * @param environment - Environment name (development, staging, production)
 * @param enabled - Whether Sentry should be enabled (defaults to true in production)
 */
export function initSentry(
  dsn: string | undefined,
  environment: string = 'development',
  enabled: boolean = true
): void {
  // Only initialize if DSN is provided and enabled
  if (!dsn || !enabled) {
    return;
  }

  Sentry.init({
    dsn,
    environment,
    
    // Performance Monitoring
    tracesSampleRate: environment === 'production' ? 0.1 : 1.0, // 10% in prod, 100% in dev
    
    // Session Replay (optional - can be expensive)
    replaysSessionSampleRate: environment === 'production' ? 0.1 : 1.0,
    replaysOnErrorSampleRate: 1.0, // Always record replays on errors
    
    // Integrations
    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.replayIntegration({
        maskAllText: true, // Mask sensitive text
        blockAllMedia: true, // Block media elements for privacy
      }),
    ],
    
    // Filter out common non-critical errors
    ignoreErrors: [
      // Browser extensions
      'top.GLOBALS',
      'originalCreateNotification',
      'canvas.contentDocument',
      'MyApp_RemoveAllHighlights',
      'atomicFindClose',
      'fb_xd_fragment',
      'bmi_SafeAddOnload',
      'EBCallBackMessageReceived',
      'conduitPage',
      // Network errors that are handled gracefully
      'NetworkError',
      'Failed to fetch',
      'Load failed',
      // Chrome extensions
      'chrome-extension://',
      'moz-extension://',
      // React 19 + DevTools compatibility issue
      'Cannot set properties of undefined (setting \'Activity\')',
      'Cannot set properties of undefined',
    ],
    
    // Filter out URLs that shouldn't be tracked
    denyUrls: [
      // Browser extensions
      /extensions\//i,
      /^chrome:\/\//i,
      /^chrome-extension:\/\//i,
      /^moz-extension:\/\//i,
    ],
    
    // Before sending event - can modify or filter events
    beforeSend(event, _hint) {
      // Don't send events in development unless it's a real error
      if (environment === 'development' && event.level === 'info') {
        return null;
      }
      
      // Add additional context
      if (event.request) {
        event.request.headers = {
          ...event.request.headers,
          // Don't log sensitive headers
        };
      }
      
      return event;
    },
    
    // Set user context (will be set dynamically when user logs in)
    initialScope: {
      tags: {
        component: 'frontend',
      },
    },
  });
}

/**
 * Set user context in Sentry
 * Call this after user logs in to associate errors with users
 */
export function setSentryUser(user: { id: string; email?: string; username?: string } | null): void {
  // Only set user if Sentry is initialized
  try {
    if (user) {
      Sentry.setUser({
        id: user.id,
        email: user.email,
        username: user.username || user.email,
      });
    } else {
      Sentry.setUser(null);
    }
  } catch (_error) {
    // Sentry not initialized, ignore
  }
}

/**
 * Add breadcrumb for navigation tracking
 */
export function addNavigationBreadcrumb(pathname: string): void {
  // Only add breadcrumb if Sentry is initialized
  try {
    Sentry.addBreadcrumb({
      category: 'navigation',
      message: `Navigated to ${pathname}`,
      level: 'info',
      data: {
        pathname,
      },
    });
  } catch (_error) {
    // Sentry not initialized, ignore
  }
}

/**
 * Add breadcrumb for API calls
 */
export function addApiBreadcrumb(
  method: string,
  url: string,
  statusCode?: number,
  error?: boolean
): void {
  // Only add breadcrumb if Sentry is initialized
  try {
    Sentry.addBreadcrumb({
      category: 'http',
      message: `${method} ${url}`,
      level: error ? 'error' : statusCode && statusCode >= 400 ? 'warning' : 'info',
      data: {
        method,
        url,
        status_code: statusCode,
      },
    });
  } catch (_error) {
    // Sentry not initialized, ignore
  }
}

/**
 * Capture exception with context
 */
export function captureException(
  error: Error,
  context?: {
    tags?: Record<string, string>;
    extra?: Record<string, unknown>;
    level?: Sentry.SeverityLevel;
  }
): string {
  return Sentry.captureException(error, {
    tags: context?.tags,
    extra: context?.extra,
    level: context?.level,
  });
}

/**
 * Capture message (non-error events)
 */
export function captureMessage(
  message: string,
  level: Sentry.SeverityLevel = 'info',
  context?: {
    tags?: Record<string, string>;
    extra?: Record<string, unknown>;
  }
): string {
  return Sentry.captureMessage(message, {
    level,
    tags: context?.tags,
    extra: context?.extra,
  });
}

