import { Outlet, Link, useLocation, useNavigate } from "react-router-dom";
import { LayoutDashboard, Server, Camera, Users, Play, History, Bell, LogOut, Menu, Activity, Cloud, CloudOff } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { useState, useEffect } from "react";
import { cn } from "../lib/utils";
import { useQuery } from "@tanstack/react-query";
import api from "../lib/api";

const CloudStatusBadge = () => {
  const { data, isLoading } = useQuery({
    queryKey: ["cloud-status"],
    queryFn: () => api.get("/system/cloud-status").then((res) => res.data),
    refetchInterval: 30000,
  });

  if (isLoading) {
    return (
      <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700">
        <Cloud className="h-3.5 w-3.5 animate-pulse" />
        <span className="hidden sm:inline">Checking Cloud...</span>
      </div>
    );
  }

  const isOnline = data?.online;

  return (
    <div className={cn(
      "flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border transition-colors cursor-default",
      isOnline 
        ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" 
        : "bg-rose-500/10 text-rose-400 border-rose-500/20"
    )} title={isOnline ? "Cloud Server Reachable" : "Cloud Server Unreachable"}>
      {isOnline ? <Cloud className="h-3.5 w-3.5" /> : <CloudOff className="h-3.5 w-3.5" />}
      <span className="hidden sm:inline">Cloud: {isOnline ? "Online" : "Offline"}</span>
    </div>
  );
};

const NavItem = ({ to, icon: Icon, children, onClick }) => {
  const location = useLocation();
  const isActive = location.pathname.startsWith(to);

  return (
    <Link
      to={to}
      onClick={onClick}
      className={cn(
        "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
        isActive ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
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
  const location = useLocation();

  // Close sidebar automatically on navigation
  useEffect(() => {
    setSidebarOpen(false);
  }, [location.pathname]);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-50 overflow-hidden">
      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-64 transform border-r border-slate-800 bg-slate-900 transition-transform lg:static lg:translate-x-0 flex flex-col",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex h-16 shrink-0 items-center justify-between border-b border-slate-800 px-6">
          <span className="text-xl font-bold tracking-tight">VMS Platform</span>
          <button onClick={() => setSidebarOpen(false)} className="lg:hidden p-1 rounded-md hover:bg-slate-800">
             <Menu className="h-5 w-5" />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto py-4">
          <nav className="flex flex-col gap-1 px-4">
            {user?.role === "admin" && (
              <>
                <NavItem to="/dashboard" icon={LayoutDashboard} onClick={() => setSidebarOpen(false)}>Dashboard</NavItem>
                <NavItem to="/sites" icon={Server} onClick={() => setSidebarOpen(false)}>Sites</NavItem>
                <NavItem to="/servers" icon={Server} onClick={() => setSidebarOpen(false)}>Local Servers</NavItem>
                <NavItem to="/cameras" icon={Camera} onClick={() => setSidebarOpen(false)}>Cameras</NavItem>
                <NavItem to="/troubleshooting" icon={Activity} onClick={() => setSidebarOpen(false)}>Troubleshooting</NavItem>
                <NavItem to="/users" icon={Users} onClick={() => setSidebarOpen(false)}>Users</NavItem>
              </>
            )}
            <NavItem to="/live" icon={Play} onClick={() => setSidebarOpen(false)}>Live Streams</NavItem>
            {user?.role === "admin" && (
              <>
                <NavItem to="/camera-history" icon={History} onClick={() => setSidebarOpen(false)}>Movement History</NavItem>
                <NavItem to="/notifications" icon={Bell} onClick={() => setSidebarOpen(false)}>Notifications</NavItem>
              </>
            )}
          </nav>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden relative">
        <header className="flex h-16 shrink-0 items-center justify-between border-b border-slate-800 bg-slate-950 px-4 lg:px-8 z-10">
          <div className="flex items-center gap-4 flex-1">
            <button onClick={() => setSidebarOpen(true)} className="p-2 lg:hidden rounded-md hover:bg-slate-800">
              <Menu className="h-6 w-6" />
            </button>
            <span className="font-bold text-lg lg:hidden hidden sm:block">VMS Platform</span>
            <div className="relative w-full max-w-sm hidden md:block">
              <input 
                type="text" 
                placeholder="Search cameras or sites..." 
                className="w-full pl-3 pr-10 py-2 border border-slate-700 bg-slate-900 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-primary text-slate-50 placeholder-slate-400"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    navigate('/search?q=' + e.target.value);
                  }
                }}
              />
            </div>
          </div>
          <div className="flex items-center gap-4">
            <CloudStatusBadge />
            <div className="flex flex-col items-end justify-center mr-2">
              <span className="text-sm font-bold">{user?.username}</span>
              <span className="text-[10px] text-slate-400 uppercase tracking-wider">{user?.role}</span>
            </div>
            <button
              onClick={handleLogout}
              className="rounded-full p-2 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
              title="Logout"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </header>
        
        <div className="flex-1 overflow-auto p-4 md:p-6 lg:p-8 relative">
          <Outlet />
        </div>
      </main>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden transition-opacity"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
}
