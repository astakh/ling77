import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useStore } from './store/useStore';
import LandingPage from './pages/LandingPage';
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

  if (user && !user.isOnboarded) {
    return <Navigate to="/onboarding" replace />;
  }

  return <>{children}</>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/admin/login" element={<AdminLoginPage />} />
        
        {/* Protected routes */}
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
        <Route path="/admin/dictionaries" element={<AdminDictionariesPage />} />
        <Route path="/admin/dictionaries/:dictionaryId" element={<AdminDictionaryWordsPage />} />
        
        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
