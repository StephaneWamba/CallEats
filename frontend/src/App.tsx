import { Routes, Route, Navigate } from 'react-router-dom';
import { useAppSelector } from '@/store/hooks';
import { ROUTES } from '@/config/routes';
import { LandingPage } from '@/pages/LandingPage';
import { LoginPage } from '@/pages/LoginPage';
import { SignUpPage } from '@/pages/SignUpPage';
import { PasswordResetPage } from '@/pages/PasswordResetPage';
import { Dashboard } from '@/pages/Dashboard';
import { MenuBuilder } from '@/pages/MenuBuilder';
import { OperatingHours } from '@/pages/OperatingHours';
import { DeliveryZones } from '@/pages/DeliveryZones';
import { CallHistory } from '@/pages/CallHistory';
import { Settings } from '@/pages/Settings';
import { Toast } from '@/components/common/Toast';

// Pages
const DashboardPage = () => <Dashboard />;
const MenuBuilderPage = () => <MenuBuilder />;
const OperatingHoursPage = () => <OperatingHours />;
const DeliveryZonesPage = () => <DeliveryZones />;
const CallHistoryPage = () => <CallHistory />;
const SettingsPage = () => <Settings />;

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = useAppSelector((state) => state.auth.isAuthenticated);

  if (!isAuthenticated) {
    return <Navigate to={ROUTES.LOGIN} replace />;
  }

  return <>{children}</>;
};

function App() {
  return (
    <>
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
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path={ROUTES.MENU_BUILDER}
          element={
            <ProtectedRoute>
              <MenuBuilderPage />
            </ProtectedRoute>
          }
        />
        <Route
          path={ROUTES.OPERATING_HOURS}
          element={
            <ProtectedRoute>
              <OperatingHoursPage />
            </ProtectedRoute>
          }
        />
        <Route
          path={ROUTES.DELIVERY_ZONES}
          element={
            <ProtectedRoute>
              <DeliveryZonesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path={ROUTES.CALL_HISTORY}
          element={
            <ProtectedRoute>
              <CallHistoryPage />
            </ProtectedRoute>
          }
        />
        <Route
          path={ROUTES.SETTINGS}
          element={
            <ProtectedRoute>
              <SettingsPage />
            </ProtectedRoute>
          }
        />

        {/* Catch all - redirect to landing */}
        <Route path="*" element={<Navigate to={ROUTES.LANDING} replace />} />
      </Routes>
      <Toast />
    </>
  );
}

export default App;

