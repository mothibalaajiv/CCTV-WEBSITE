import { Outlet, Link, useLocation, useNavigate } from "react-router-dom";
import { LayoutDashboard, Server, Camera, Users, Play, History, Bell, LogOut, Menu } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { useState } from "react";
import { cn } from "../lib/utils";

const NavItem = ({ to, icon: Icon, children }) => {
  const location = useLocation();
  const isActive = location.pathname.startsWith(to);

  return (
    <Link
      to={to}
      className={cn(
        "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
        isActive ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-muted hover:text-foreground"
      )}
    >
      <Icon className="h-4 w-4" />
      {children}
    </Link>
  );
};

export default function MainLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="flex min-h-screen flex-col lg:flex-row bg-background">
      {/* Mobile Header */}
      <div className="flex h-16 items-center justify-between border-b px-4 lg:hidden">
        <span className="font-bold">VMS Platform</span>
        <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2">
          <Menu className="h-6 w-6" />
        </button>
      </div>

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-64 transform border-r bg-card transition-transform lg:static lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex h-16 items-center border-b px-6">
          <span className="text-lg font-bold">VMS Platform</span>
        </div>
        <div className="flex flex-col gap-1 p-4">
          <NavItem to="/dashboard" icon={LayoutDashboard}>Dashboard</NavItem>
          <NavItem to="/sites" icon={Server}>Sites</NavItem>
          <NavItem to="/servers" icon={Server}>Local Servers</NavItem>
          <NavItem to="/cameras" icon={Camera}>Cameras</NavItem>
          {user?.role === "admin" && (
            <NavItem to="/users" icon={Users}>Users</NavItem>
          )}
          <NavItem to="/live" icon={Play}>Live Streams</NavItem>
          <NavItem to="/camera-history" icon={History}>Movement History</NavItem>
          <NavItem to="/notifications" icon={Bell}>Notifications</NavItem>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0">
        <header className="flex h-16 items-center justify-between border-b px-6 lg:px-8">
          <div className="flex items-center gap-4 flex-1">
            <div className="relative w-full max-w-sm">
              <input 
                type="text" 
                placeholder="Search cameras or sites..." 
                className="w-full pl-3 pr-10 py-2 border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-primary"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    // Quick mock navigation, ideally an autocomplete dropdown
                    navigate('/search?q=' + e.target.value);
                  }
                }}
              />
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex flex-col items-end justify-center mr-2">
              <span className="text-sm font-bold">{user?.username}</span>
              <span className="text-xs text-muted-foreground uppercase">{user?.role}</span>
            </div>
            <button
              onClick={handleLogout}
              className="rounded-full p-2 hover:bg-muted"
              title="Logout"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </header>
        <div className="flex-1 p-6 lg:p-8 overflow-auto">
          <Outlet />
        </div>
      </main>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
}
