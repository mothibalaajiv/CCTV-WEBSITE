import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import api from "../../lib/api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../components/ui/table";
import { Button } from "../../components/ui/button";

export default function LocalServers() {
  const queryClient = useQueryClient();
  const { data: servers, isLoading } = useQuery({
    queryKey: ["servers"],
    queryFn: () => api.get("/servers").then((res) => res.data),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => api.delete(`/servers/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["servers"] })
  });

  const toggleStatusMutation = useMutation({
    mutationFn: ({ id, is_active }) => api.put(`/servers/${id}/status`, { is_active }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["servers"] })
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Local Servers</h1>
        <Link to="/servers/register">
          <Button>Register Local Server</Button>
        </Link>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Server ID</TableHead>
              <TableHead>MAC Address</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow><TableCell colSpan={4} className="text-center">Loading...</TableCell></TableRow>
            ) : servers?.length ? (
              servers.map((server) => (
                <TableRow key={server._id}>
                  <TableCell className="font-medium">{server.server_id}</TableCell>
                  <TableCell>{server.mac_address}</TableCell>
                  <TableCell>
                    {!server.is_active ? (
                      <span className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold bg-red-100 text-red-800">
                        Deactivated
                      </span>
                    ) : server.status === 'online' ? (
                      <span className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold bg-green-100 text-green-800">
                        Online
                      </span>
                    ) : (
                      <span className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold bg-gray-100 text-gray-800">
                        Offline
                      </span>
                    )}
                  </TableCell>
                  <TableCell className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => toggleStatusMutation.mutate({ id: server._id, is_active: !server.is_active })}>
                      {server.is_active ? "Deactivate" : "Activate"}
                    </Button>
                    <Button variant="destructive" size="sm" onClick={() => deleteMutation.mutate(server._id)}>Delete</Button>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow><TableCell colSpan={4} className="text-center">No local servers found.</TableCell></TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
