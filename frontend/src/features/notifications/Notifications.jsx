import { useQuery } from "@tanstack/react-query";
import api from "../../lib/api";
import { Card, CardContent } from "../../components/ui/card";
import { Bell } from "lucide-react";

export default function Notifications() {
  const { data: notifications, isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => api.get("/system/notifications").then((res) => res.data),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Notifications</h1>
      </div>

      <div className="space-y-4">
        {isLoading ? (
          <div>Loading...</div>
        ) : notifications?.length ? (
          notifications.map((note) => (
            <Card key={note.id} className={note.read ? "opacity-75" : ""}>
              <CardContent className="flex items-start gap-4 p-4">
                <Bell className={`mt-1 h-5 w-5 ${note.read ? "text-muted-foreground" : "text-primary"}`} />
                <div className="flex-1 space-y-1">
                  <p className="text-sm font-medium leading-none">{note.type}</p>
                  <p className="text-sm text-muted-foreground">{note.message}</p>
                  <p className="text-xs text-muted-foreground">{new Date(note.timestamp).toLocaleString()}</p>
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <p>No notifications.</p>
        )}
      </div>
    </div>
  );
}
