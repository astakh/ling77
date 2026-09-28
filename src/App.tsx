import { useEffect } from 'react';
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useStore } from './store/useStore';
import AuthPage from './pages/AuthPage';
import OnboardingPage from './pages/OnboardingPage';
import DashboardPage from './pages/DashboardPage';
import LessonPreviewPage from './pages/LessonPreviewPage';
import ExercisePage from './pages/ExercisePage';
import LessonSummaryPage from './pages/LessonSummaryPage';
import VocabularyPage from './pages/VocabularyPage';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, user } = useStore();

  if (!isAuthenticated) {
    return <Navigate to="/auth" replace />;
  }

  if (user && !user.isOnboarded) {
    return <Navigate to="/onboarding" replace />;
  }

  return <>{children}</>;
}

function OnboardingGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, user } = useStore();

  if (!isAuthenticated) {
    return <Navigate to="/auth" replace />;
  }

  if (user?.isOnboarded) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}

function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, user } = useStore();

  if (isAuthenticated && user?.isOnboarded) {
    return <Navigate to="/dashboard" replace />;
  }

  if (isAuthenticated && user && !user.isOnboarded) {
    return <Navigate to="/onboarding" replace />;
  }

  return <>{children}</>;
}

function App() {
  const { initialize } = useStore();

  useEffect(() => {
    initialize();
  }, [initialize]);

  return (
    <HashRouter>
      <Routes>
        <Route path="/auth" element={
          <AuthGuard>
            <AuthPage />
          </AuthGuard>
        } />
        <Route path="/onboarding" element={
          <OnboardingGuard>
            <OnboardingPage />
          </OnboardingGuard>
        } />
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        } />
        <Route path="/lesson/preview" element={
          <ProtectedRoute>
            <LessonPreviewPage />
          </ProtectedRoute>
        } />
        <Route path="/lesson/exercise" element={
          <ProtectedRoute>
            <ExercisePage />
          </ProtectedRoute>
        } />
        <Route path="/lesson/summary" element={
          <ProtectedRoute>
            <LessonSummaryPage />
          </ProtectedRoute>
        } />
        <Route path="/vocabulary" element={
          <ProtectedRoute>
            <VocabularyPage />
          </ProtectedRoute>
        } />
        <Route path="*" element={<Navigate to="/auth" replace />} />
      </Routes>
    </HashRouter>
  );
}

export default App;
