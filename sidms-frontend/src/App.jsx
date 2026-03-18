import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import VerifyEmail from "./pages/VerifyEmail";
import OtpVerification from "./pages/OtpVerification";
import Dashboard from "./pages/Dashboard";
import ProfileForm from "./pages/ProfileForm";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminDashboard from "./pages/AdminDashboard";
import AdminStudentDetail from "./pages/AdminStudentDetail";
import AuditLogs from "./pages/AuditLogs";

function App() {
  return (
    <Routes>
      {/* ── Public Routes ─────────────────────── */}
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/verify" element={<VerifyEmail />} />
      <Route path="/otp" element={<OtpVerification />} />

      {/* ── Authenticated Routes ──────────────── */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <ProfileForm />
          </ProtectedRoute>
        }
      />
      <Route
        path="/profileform"
        element={
          <ProtectedRoute>
            <ProfileForm />
          </ProtectedRoute>
        }
      />
      <Route
        path="/complete-profile"
        element={
          <ProtectedRoute roles={["ROLE_MEMBER"]}>
            <ProfileForm />
          </ProtectedRoute>
        }
      />

      {/* ── Admin Routes ─────────────────────── */}
      <Route
        path="/admin-dashboard"
        element={
          <ProtectedRoute roles={["ROLE_ADMIN"]}>
            <AdminDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/student/:studentId"
        element={
          <ProtectedRoute roles={["ROLE_ADMIN"]}>
            <AdminStudentDetail />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/audit-logs"
        element={
          <ProtectedRoute roles={["ROLE_ADMIN"]}>
            <AuditLogs />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default App;