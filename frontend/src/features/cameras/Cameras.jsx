import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../../lib/api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../components/ui/table";
import { Button } from "../../components/ui/button";
import { Link } from "react-router-dom";

export default function Cameras() {
  const queryClient = useQueryClient();
  const { data: cameras, isLoading } = useQuery({
    queryKey: ["cameras"],
    queryFn: () => api.get("/cameras").then((res) => res.data),
  });

  const { data: sites } = useQuery({
    queryKey: ["sites"],
    queryFn: () => api.get("/sites").then((res) => res.data),
  });

  const { data: streams } = useQuery({
    queryKey: ["streams"],
    queryFn: () => api.get("/streams").then((res) => res.data),
  });

  const updateSiteMutation = useMutation({
    mutationFn: ({ id, siteId }) => api.put(`/cameras/${id}`, { current_site: siteId }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["cameras"] })
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => api.delete(`/cameras/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["cameras"] })
  });

  const toggleStatusMutation = useMutation({
    mutationFn: ({ id, is_active }) => api.put(`/cameras/${id}/status`, { is_active }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["cameras", "streams"] })
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Cameras</h1>
        <Link to="/cameras/register">
          <Button>Register Camera</Button>
        </Link>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Camera Code</TableHead>
              <TableHead>MAC Address</TableHead>
              <TableHead>Location</TableHead>
              <TableHead>Stream Status</TableHead>
              <TableHead>Active</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow><TableCell colSpan={6} className="text-center">Loading...</TableCell></TableRow>
            ) : cameras?.length ? (
              cameras.map((camera) => {
                const isOnline = streams?.some(s => s.camera_code === camera.camera_code);
                const streamStatus = isOnline ? 'online' : 'offline';
                return (
                <TableRow key={camera._id}>
                  <TableCell className="font-medium">{camera.camera_code}</TableCell>
                  <TableCell>{camera.mac_address}</TableCell>
                  <TableCell>{camera.location_name}</TableCell>
                  <TableCell>
                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${streamStatus === 'online' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {streamStatus}
                    </span>
                  </TableCell>
                  <TableCell>
                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${camera.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                      {camera.is_active ? "Active" : "Inactive"}
                    </span>
                  </TableCell>
                  <TableCell className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => toggleStatusMutation.mutate({ id: camera._id, is_active: !camera.is_active })}>
                      {camera.is_active ? "Deactivate" : "Activate"}
                    </Button>
                    <Button variant="destructive" size="sm" onClick={() => deleteMutation.mutate(camera._id)}>Delete</Button>
                  </TableCell>
                </TableRow>
                );
              })
            ) : (
              <TableRow><TableCell colSpan={6} className="text-center">No cameras found.</TableCell></TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
