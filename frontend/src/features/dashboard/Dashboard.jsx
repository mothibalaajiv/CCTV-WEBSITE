import { useQuery } from "@tanstack/react-query";
import api from "../../lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Server, Camera, PlayCircle, AlertCircle, Users } from "lucide-react";

export default function Dashboard() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: () => api.get("/system/dashboard").then((res) => res.data),
  });

  if (isLoading) return <div>Loading dashboard...</div>;

  const activeStreams = stats?.active_streams || 0;
  const offlineCameras = (stats?.total_cameras || 0) - activeStreams; // Simple heuristic for now

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_users || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Sites</CardTitle>
            <Server className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_sites || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Cameras</CardTitle>
            <Camera className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_cameras || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Active Streams</CardTitle>
            <PlayCircle className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{activeStreams}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Offline Cameras</CardTitle>
            <AlertCircle className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{offlineCameras}</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Recent Camera Movements</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-8">
              {stats?.recent_movements?.map((movement, i) => (
                <div key={movement._id || i} className="flex items-center">
                  <div className="ml-4 space-y-1">
                    <p className="text-sm font-medium leading-none">
                      Camera {movement.camera_code}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Moved from {movement.old_site || "N/A"} to {movement.new_site || "N/A"}
                    </p>
                  </div>
                  <div className="ml-auto font-medium">
                    {new Date(movement.moved_at).toLocaleDateString()}
                  </div>
                </div>
              ))}
              {(!stats?.recent_movements || stats.recent_movements.length === 0) && (
                <p className="text-sm text-muted-foreground">No recent movements.</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
