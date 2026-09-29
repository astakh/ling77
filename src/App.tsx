import { useEffect, useState } from 'react';
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useStore } from './store/useStore';
import AuthPage from './pages/AuthPage';
import OnboardingPage from './pages/OnboardingPage';
import DashboardPage from './pages/DashboardPage';
import LessonPreviewPage from './pages/LessonPreviewPage';
import ExercisePage from './pages/ExercisePage';
import LessonSummaryPage from './pages/LessonSummaryPage';
import VocabularyPage from './pages/VocabularyPage';
import DictionariesPage from './pages/DictionariesPage';
import SettingsPage from './pages/SettingsPage';
import AdminLoginPage from './pages/AdminLoginPage';
import AdminDictionariesPage from './pages/AdminDictionariesPage';
import AdminDictionaryWordsPage from './pages/AdminDictionaryWordsPage';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, user } = useStore();

  if (!isAuthenticated) {
    return <Navigate to="/auth" replace />;
  }

  // If user is authenticated but not onboarded, redirect to onboarding
  if (user && !user.isOnboarded) {
    return <Navigate to="/onboarding" replace />;
  }

  return <>{children}</>;
}

function App() {
  const { initialize, isAuthenticated, user } = useStore();
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    const init = async () => {
      await initialize();
      setIsInitialized(true);
    };
    init();
  }, [initialize]);

  if (!isInitialized) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-500">Загрузка...</div>
      </div>
    );
  }

  return (
    <HashRouter>
      <Routes>
        <Route path="/auth" element={
          isAuthenticated 
            ? (user?.isOnboarded 
                ? <Navigate to="/dashboard" replace /> 
                : <Navigate to="/onboarding" replace />)
            : <AuthPage />
        } />
        <Route path="/onboarding" element={
          <ProtectedRoute>
            <OnboardingPage />
          </ProtectedRoute>
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
        <Route path="/dictionaries" element={
          <ProtectedRoute>
            <DictionariesPage />
          </ProtectedRoute>
        } />
        <Route path="/settings" element={
          <ProtectedRoute>
            <SettingsPage />
          </ProtectedRoute>
        } />
        
        {/* Admin routes */}
        <Route path="/admin/login" element={<AdminLoginPage />} />
        <Route path="/admin/dictionaries" element={<AdminDictionariesPage />} />
        <Route path="/admin/dictionaries/:dictionaryId" element={<AdminDictionaryWordsPage />} />
        
        <Route path="*" element={<Navigate to={isAuthenticated ? "/dashboard" : "/auth"} replace />} />
      </Routes>
    </HashRouter>
  );
}

export default App;
