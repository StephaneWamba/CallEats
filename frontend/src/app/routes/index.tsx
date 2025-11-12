import { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { ROUTES } from '@/config/routes';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';

// Helper function to create lazy imports with error handling
const createLazyImport = (importFn: () => Promise<any>, componentName: string) => {
  return lazy(() =>
    importFn()
      .then((m) => ({ default: m[componentName] }))
      .catch((error) => {
        console.error(`Failed to load ${componentName}:`, error);
        // Return a fallback error component
        return {
          default: () => (
            <div className="flex min-h-screen items-center justify-center">
              <div className="text-center">
                <h2 className="text-xl font-semibold text-gray-900 mb-2">Failed to load page</h2>
                <p className="text-gray-600 mb-4">Please refresh the page to try again.</p>
                <button
                  onClick={() => window.location.reload()}
                  className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90"
                >
                  Refresh Page
                </button>
              </div>
            </div>
          ),
        };
      })
  );
};

// Lazy load all page components for code splitting
// Using dynamic imports with proper error handling
const LandingPage = createLazyImport(() => import('@/pages/LandingPage'), 'LandingPage');
const LoginPage = createLazyImport(() => import('@/pages/LoginPage'), 'LoginPage');
const SignUpPage = createLazyImport(() => import('@/pages/SignUpPage'), 'SignUpPage');
const PasswordResetPage = createLazyImport(() => import('@/pages/PasswordResetPage'), 'PasswordResetPage');
const Dashboard = createLazyImport(() => import('@/pages/Dashboard'), 'Dashboard');
const MenuBuilder = createLazyImport(() => import('@/pages/MenuBuilder'), 'MenuBuilder');
const OperatingHours = createLazyImport(() => import('@/pages/OperatingHours'), 'OperatingHours');
const DeliveryZones = createLazyImport(() => import('@/pages/DeliveryZones'), 'DeliveryZones');
const CallHistory = createLazyImport(() => import('@/pages/CallHistory'), 'CallHistory');
const Settings = createLazyImport(() => import('@/pages/Settings'), 'Settings');

// Loading fallback component
const PageLoader = () => (
  <div className="flex min-h-screen items-center justify-center">
    <LoadingSpinner size="lg" />
  </div>
);

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to={ROUTES.LOGIN} replace />;
  }

  return <>{children}</>;
};

// Route definitions
export const AppRoutes = () => {
  return (
    <ErrorBoundary>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          {/* Public Routes */}
          <Route path={ROUTES.LANDING} element={<LandingPage />} />
          <Route path={ROUTES.LOGIN} element={<LoginPage />} />
          <Route path={ROUTES.SIGNUP} element={<SignUpPage />} />
          <Route path={ROUTES.PASSWORD_RESET} element={<PasswordResetPage />} />

          {/* Protected Routes */}
          <Route
            path={ROUTES.DASHBOARD}
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path={ROUTES.MENU_BUILDER}
            element={
              <ProtectedRoute>
                <MenuBuilder />
              </ProtectedRoute>
            }
          />
          <Route
            path={ROUTES.OPERATING_HOURS}
            element={
              <ProtectedRoute>
                <OperatingHours />
              </ProtectedRoute>
            }
          />
          <Route
            path={ROUTES.DELIVERY_ZONES}
            element={
              <ProtectedRoute>
                <DeliveryZones />
              </ProtectedRoute>
            }
          />
          <Route
            path={ROUTES.CALL_HISTORY}
            element={
              <ProtectedRoute>
                <CallHistory />
              </ProtectedRoute>
            }
          />
          <Route
            path={ROUTES.SETTINGS}
            element={
              <ProtectedRoute>
                <Settings />
              </ProtectedRoute>
            }
          />

          {/* Catch all - redirect to landing */}
          <Route path="*" element={<Navigate to={ROUTES.LANDING} replace />} />
        </Routes>
      </Suspense>
    </ErrorBoundary>
  );
};

