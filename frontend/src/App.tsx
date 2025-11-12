import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Toast } from '@/components/common/Toast';
import { ToastProvider } from '@/contexts/ToastContext';
import { AuthProvider } from '@/contexts/AuthContext';
import { AppRoutes } from '@/app/routes';
import { addNavigationBreadcrumb } from '@/config/sentry';

// Component to track navigation for Sentry
const NavigationTracker = () => {
  const location = useLocation();

  useEffect(() => {
    // Track navigation in Sentry breadcrumbs
    addNavigationBreadcrumb(location.pathname);
  }, [location.pathname]);

  return null;
};

function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <NavigationTracker />
        <AppRoutes />
        <Toast />
      </AuthProvider>
    </ToastProvider>
  );
}

export default App;

