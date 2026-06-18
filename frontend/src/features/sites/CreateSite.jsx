import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import api from "../../lib/api";
import { Button } from "../../components/ui/button";

export default function CreateSite() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { data: users } = useQuery({
    queryKey: ["users"],
    queryFn: () => api.get("/users").then(res => res.data)
  });

  const { data: servers } = useQuery({
    queryKey: ["servers"],
    queryFn: () => api.get("/servers").then(res => res.data)
  });

  const { data: sites } = useQuery({
    queryKey: ["sites"],
    queryFn: () => api.get("/sites").then(res => res.data)
  });

  const [formData, setFormData] = useState({
    site_id: "",
    site_name: "",
    local_server_id: "",
    assigned_user: ""
  });

  const mutation = useMutation({
    mutationFn: (data) => api.post("/sites", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sites"] });
      navigate("/sites");
    },
    onError: (err) => {
      alert(err.response?.data?.message || "Error creating site");
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  const mappedServerIds = sites?.map(s => s.local_server_id).filter(Boolean) || [];
  const availableServers = servers?.filter(s => !mappedServerIds.includes(s.server_id)) || [];

  return (
    <div className="max-w-md mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Create New Site</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Site ID</label>
          <input
            required
            className="w-full p-2 border rounded"
            value={formData.site_id}
            onChange={(e) => setFormData({ ...formData, site_id: e.target.value })}
            placeholder="e.g. SITE1"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Site Name</label>
          <input
            required
            className="w-full p-2 border rounded"
            value={formData.site_name}
            onChange={(e) => setFormData({ ...formData, site_name: e.target.value })}
            placeholder="e.g. Factory A"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Assign Local Server</label>
          <select
            className="w-full p-2 border rounded bg-slate-900 text-white"
            value={formData.local_server_id}
            onChange={(e) => setFormData({ ...formData, local_server_id: e.target.value })}
          >
            <option value="" className="bg-slate-900 text-white">Select Local Server</option>
            {availableServers.map(server => (
              <option key={server.server_id} value={server.server_id} className="bg-slate-900 text-white">
                Server {server.server_id} ({server.mac_address})
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Assign User</label>
          <select
            className="w-full p-2 border rounded bg-slate-900 text-white"
            value={formData.assigned_user}
            onChange={(e) => setFormData({ ...formData, assigned_user: e.target.value })}
          >
            <option value="" className="bg-slate-900 text-white">Select User</option>
            {users?.map(user => (
              <option key={user._id} value={user._id} className="bg-slate-900 text-white">
                {user.username} ({user.role})
              </option>
            ))}
          </select>
        </div>
        <div className="flex justify-end space-x-2">
          <Button variant="outline" type="button" onClick={() => navigate("/sites")}>Cancel</Button>
          <Button type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? "Creating..." : "Create Site"}
          </Button>
        </div>
      </form>
    </div>
  );
}
