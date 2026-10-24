import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./hooks/useAuth";
import AuthLayout from "./layouts/AuthLayout";
import MainLayout from "./layouts/MainLayout";
import { ProtectedRoute } from "./routes/ProtectedRoute";

// Lazy load or import directly. Let's import directly for now.
import Login from "./features/auth/Login";
import Dashboard from "./features/dashboard/Dashboard";
import Sites from "./features/sites/Sites";
import CreateSite from "./features/sites/CreateSite";
import Cameras from "./features/cameras/Cameras";
import CameraRegister from "./features/cameras/CameraRegister";
import Users from "./features/users/Users";
import CreateUser from "./features/users/CreateUser";
import LiveStreams from "./features/live/LiveStreams";
import CameraHistory from "./features/history/CameraHistory";
import Notifications from "./features/notifications/Notifications";
import SearchResults from "./features/search/SearchResults";

import LocalServers from "./features/servers/LocalServers";
import LocalServerRegister from "./features/servers/LocalServerRegister";
import ServerDiagnostics from "./features/servers/ServerDiagnostics";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<Login />} />
          </Route>

          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route element={<MainLayout />}>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/sites" element={<Sites />} />
              <Route path="/sites/create" element={<CreateSite />} />
              <Route path="/cameras" element={<Cameras />} />
              <Route path="/cameras/register" element={<CameraRegister />} />
              <Route path="/servers" element={<LocalServers />} />
              <Route path="/servers/register" element={<LocalServerRegister />} />
              <Route path="/troubleshooting" element={<ServerDiagnostics />} />
              <Route path="/live" element={<LiveStreams />} />
              <Route path="/camera-history" element={<CameraHistory />} />
              <Route path="/notifications" element={<Notifications />} />
              <Route path="/search" element={<SearchResults />} />

              {/* Admin Only Routes */}
              <Route element={<ProtectedRoute allowedRoles={["admin"]} />}>
                <Route path="/users" element={<Users />} />
                <Route path="/users/create" element={<CreateUser />} />
              </Route>
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
