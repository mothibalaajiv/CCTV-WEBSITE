import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../../lib/api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../components/ui/table";
import { Button } from "../../components/ui/button";
import { Link } from "react-router-dom";

export default function Sites() {
  const queryClient = useQueryClient();
  const { data: sites, isLoading } = useQuery({
    queryKey: ["sites"],
    queryFn: () => api.get("/sites").then((res) => res.data),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => api.delete(`/sites/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["sites"] })
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Sites</h1>
        <Link to="/sites/create"><Button>Add Site</Button></Link>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Site ID</TableHead>
              <TableHead>Site Name</TableHead>
              <TableHead>Local Server ID</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow><TableCell colSpan={6} className="text-center">Loading...</TableCell></TableRow>
            ) : sites?.length ? (
              sites.map((site) => (
                <TableRow key={site._id}>
                  <TableCell className="font-medium">{site.site_id}</TableCell>
                  <TableCell>{site.site_name}</TableCell>
                  <TableCell>{site.local_server_id || "Unassigned"}</TableCell>
                  <TableCell>{site.assigned_users?.join(", ") || "None"}</TableCell>
                  <TableCell>
                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${site.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {site.status}
                    </span>
                  </TableCell>
                  <TableCell>
                    <Button variant="destructive" size="sm" onClick={() => deleteMutation.mutate(site._id)}>Delete</Button>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow><TableCell colSpan={5} className="text-center">No sites found.</TableCell></TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
