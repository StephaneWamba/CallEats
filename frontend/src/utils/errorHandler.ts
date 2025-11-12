
/**
 * Standardized error response shape from the API
 */
export interface StandardizedError {
  message: string;
  statusCode?: number;
  code?: string;
  details?: Record<string, string[]>;
  originalError?: unknown;
}

/**
 * FastAPI error response structure
 */
interface FastAPIErrorResponse {
  detail?: string | Array<{ msg?: string; message?: string; loc?: string[]; type?: string }> | Record<string, string[]>;
  message?: string;
  error?: string;
}

/**
 * Axios error with FastAPI response structure
 */
interface AxiosFastAPIError {
  isAxiosError?: boolean;
  code?: string;
  message?: string;
  response?: {
    data?: FastAPIErrorResponse;
    status?: number;
    statusText?: string;
  };
}

/**
 * Extract error message from FastAPI validation error detail
 */
function extractFastAPIDetail(detail: FastAPIErrorResponse['detail']): string {
  if (!detail) return '';

  // String detail
  if (typeof detail === 'string') {
    return detail;
  }

  // Array of validation errors
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === 'string') {
          return item;
        }
        if (typeof item === 'object' && item !== null) {
          // FastAPI validation error format: { msg, loc, type }
          return item.msg || item.message || JSON.stringify(item);
        }
        return String(item);
      })
      .filter(Boolean)
      .join(', ');
  }

  // Object with field names as keys
  if (typeof detail === 'object' && detail !== null) {
    const messages: string[] = [];
    for (const [field, errors] of Object.entries(detail)) {
      if (Array.isArray(errors)) {
        messages.push(`${field}: ${errors.join(', ')}`);
      } else {
        messages.push(`${field}: ${String(errors)}`);
      }
    }
    return messages.join('; ');
  }

  return String(detail);
}

/**
 * Extract error message from Axios error response
 */
function extractAxiosErrorMessage(error: AxiosFastAPIError): string {
  const responseData = error.response?.data;

  if (!responseData) {
    // Network error or no response
    if (error.code === 'ECONNABORTED') {
      return 'Request timeout. Please try again.';
    }
    if (error.code === 'ERR_NETWORK') {
      return 'Network error. Please check your connection.';
    }
    return error.message || 'An unexpected error occurred';
  }

  // Try FastAPI detail first (most common)
  if (responseData.detail) {
    const detailMessage = extractFastAPIDetail(responseData.detail);
    if (detailMessage) {
      return detailMessage;
    }
  }

  // Try message field
  if (responseData.message) {
    return String(responseData.message);
  }

  // Try error field
  if (responseData.error) {
    return String(responseData.error);
  }

  // Fallback to status text or generic message
  return error.response?.statusText || 'An error occurred';
}

/**
 * Get HTTP status code from error
 */
function getStatusCode(error: unknown): number | undefined {
  if (error && typeof error === 'object' && 'response' in error) {
    const axiosError = error as AxiosFastAPIError;
    return axiosError.response?.status;
  }
  return undefined;
}

/**
 * Centralized error handler that standardizes error shapes
 * 
 * @param error - The error to handle (can be AxiosError, Error, or unknown)
 * @param defaultMessage - Optional default message if error cannot be parsed
 * @returns Standardized error object with consistent shape
 * 
 * @example
 * ```ts
 * try {
 *   await apiCall();
 * } catch (error) {
 *   const standardized = handleError(error, 'Operation failed');
 *   console.error(standardized.message);
 *   showToast(standardized.message);
 * }
 * ```
 */
export function handleError(
  error: unknown,
  defaultMessage: string = 'An unexpected error occurred',
  options?: {
    logToSentry?: boolean;
    sentryContext?: {
      tags?: Record<string, string>;
      extra?: Record<string, unknown>;
      level?: 'error' | 'warning' | 'info';
    };
  }
): StandardizedError {
  let standardized: StandardizedError;
  
  // Axios error (most common in API calls)
  if (error && typeof error === 'object' && 'isAxiosError' in error) {
    const axiosError = error as AxiosFastAPIError;
    const message = extractAxiosErrorMessage(axiosError);
    const statusCode = getStatusCode(axiosError);
    
    // Extract details if available
    let details: Record<string, string[]> | undefined;
    const responseData = axiosError.response?.data;
    if (responseData?.detail && typeof responseData.detail === 'object' && !Array.isArray(responseData.detail)) {
      const detailObj = responseData.detail as Record<string, string[]>;
      details = {};
      for (const [key, value] of Object.entries(detailObj)) {
        details[key] = Array.isArray(value) ? value : [String(value)];
      }
    }

    standardized = {
      message: message || defaultMessage,
      statusCode,
      code: axiosError.code,
      details,
      originalError: error,
    };
  } else if (error instanceof Error) {
  // Standard Error object
    standardized = {
      message: error.message || defaultMessage,
      code: error.name,
      originalError: error,
    };
  } else if (typeof error === 'string') {
  // String error
    standardized = {
      message: error || defaultMessage,
      originalError: error,
    };
  } else {
  // Unknown error type
    standardized = {
    message: defaultMessage,
    originalError: error,
  };
  }

  // Log to Sentry if enabled (default: only log server errors and unexpected errors)
  const shouldLog = options?.logToSentry !== false && (
    // Always log server errors (5xx)
    (standardized.statusCode !== undefined && standardized.statusCode >= 500) ||
    // Always log unexpected errors (no status code)
    (standardized.statusCode === undefined && !standardized.code) ||
    // Log if explicitly requested
    options?.logToSentry === true
  );

  if (shouldLog) {
    logErrorToSentry(error, options?.sentryContext);
  }

  return standardized;
}

/**
 * Extract just the error message string (for simpler use cases)
 * 
 * @param error - The error to handle
 * @param defaultMessage - Optional default message
 * @returns Error message string
 * 
 * @example
 * ```ts
 * try {
 *   await apiCall();
 * } catch (error) {
 *   const message = getErrorMessage(error, 'Operation failed');
 *   setError(message);
 * }
 * ```
 */
export function getErrorMessage(
  error: unknown,
  defaultMessage: string = 'An unexpected error occurred'
): string {
  return handleError(error, defaultMessage).message;
}

/**
 * Check if error is a specific HTTP status code
 */
export function isErrorStatus(error: unknown, statusCode: number): boolean {
  const standardized = handleError(error);
  return standardized.statusCode === statusCode;
}

/**
 * Check if error is a network error
 */
export function isNetworkError(error: unknown): boolean {
  if (error && typeof error === 'object' && 'isAxiosError' in error) {
    const axiosError = error as AxiosFastAPIError;
    return axiosError.code === 'ERR_NETWORK' || axiosError.code === 'ECONNABORTED';
  }
  return false;
}

/**
 * Check if error is an authentication error (401)
 */
export function isAuthError(error: unknown): boolean {
  return isErrorStatus(error, 401);
}

/**
 * Check if error is a forbidden error (403)
 */
export function isForbiddenError(error: unknown): boolean {
  return isErrorStatus(error, 403);
}

/**
 * Check if error is a not found error (404)
 */
export function isNotFoundError(error: unknown): boolean {
  return isErrorStatus(error, 404);
}

/**
 * Check if error is a validation error (422)
 */
export function isValidationError(error: unknown): boolean {
  return isErrorStatus(error, 422);
}
/**
 * Check if error is a server error (5xx)
 */
export function isServerError(error: unknown): boolean {
  const standardized = handleError(error);
  return standardized.statusCode !== undefined && standardized.statusCode >= 500;
}

/**
 * Log error to Sentry (if available)
 * This is called automatically by handleError, but can be called manually for specific errors
 * Uses dynamic import to avoid circular dependencies
 */
export function logErrorToSentry(
  error: unknown,
  context?: {
    tags?: Record<string, string>;
    extra?: Record<string, unknown>;
    level?: 'error' | 'warning' | 'info';
  }
): void {
  // Dynamic import to avoid issues if Sentry is not configured
  try {
    // Only log if Sentry is available (check for Sentry global)
    if (typeof window !== 'undefined') {
      import('@sentry/react').then((Sentry) => {
        // Check if Sentry is initialized by checking if captureException exists
        if (!Sentry || typeof Sentry.captureException !== 'function') {
          return;
        }

        // Standardize error without calling handleError to avoid recursion
        let errorObj: Error;
        let errorMessage: string;
        let statusCode: number | undefined;
        let errorCode: string | undefined;

        if (error instanceof Error) {
          errorObj = error;
          errorMessage = error.message;
          errorCode = error.name;
        } else if (error && typeof error === 'object' && 'isAxiosError' in error) {
          const axiosError = error as any;
          errorMessage = axiosError.response?.data?.detail || axiosError.message || 'API Error';
          statusCode = axiosError.response?.status;
          errorCode = axiosError.code;
          errorObj = new Error(errorMessage);
        } else {
          errorMessage = String(error || 'Unknown error');
          errorObj = new Error(errorMessage);
        }

        Sentry.captureException(errorObj, {
          tags: {
            ...context?.tags,
            error_type: errorCode || 'unknown',
            status_code: statusCode?.toString() || 'unknown',
          },
          extra: {
            ...context?.extra,
            error_message: errorMessage,
            original_error: error,
          },
          level: context?.level || (statusCode && statusCode >= 500 ? 'error' : 'warning'),
        });
      }).catch(() => {
        // Sentry not available, silently fail
      });
    }
  } catch {
    // Sentry not available, silently fail
  }
}

