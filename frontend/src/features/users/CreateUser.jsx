import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import api from "../../lib/api";
import { Button } from "../../components/ui/button";

export default function CreateUser() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    username: "",
    password: "",
    role: "user",
    assigned_sites: [],
  });

  const { data: sites } = useQuery({
    queryKey: ["sites"],
    queryFn: () => api.get("/sites").then(res => res.data)
  });

  const mutation = useMutation({
    mutationFn: (data) => api.post("/users", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      navigate("/users");
    },
    onError: (err) => {
      alert(err.response?.data?.message || "Error creating user");
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  return (
    <div className="max-w-md mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Create New User</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Username</label>
          <input
            required
            className="w-full p-2 border rounded"
            value={formData.username}
            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Password</label>
          <input
            required
            type="password"
            className="w-full p-2 border rounded"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Role</label>
          <select
            className="w-full p-2 border rounded bg-slate-900 text-white"
            value={formData.role}
            onChange={(e) => setFormData({ ...formData, role: e.target.value })}
          >
            <option value="user" className="bg-slate-900 text-white">User</option>
            <option value="admin" className="bg-slate-900 text-white">Admin</option>
            <option value="security" className="bg-slate-900 text-white">Security</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Assign Sites</label>
          <div className="space-y-2 max-h-40 overflow-y-auto p-3 border rounded border-slate-800 bg-slate-900/50">
            {sites?.map(site => (
              <label key={site.site_id} className="flex items-center space-x-3 cursor-pointer p-1 hover:bg-slate-800/50 rounded">
                <input
                  type="checkbox"
                  className="w-4 h-4 rounded border-slate-700 bg-slate-800 text-blue-500 focus:ring-blue-500 focus:ring-offset-slate-900"
                  checked={formData.assigned_sites.includes(site.site_id)}
                  onChange={(e) => {
                    const checked = e.target.checked;
                    setFormData(prev => ({
                      ...prev,
                      assigned_sites: checked 
                        ? [...prev.assigned_sites, site.site_id]
                        : prev.assigned_sites.filter(id => id !== site.site_id)
                    }));
                  }}
                />
                <span className="text-sm text-slate-300">{site.site_name} <span className="text-slate-500 text-xs">(Site {site.site_id})</span></span>
              </label>
            ))}
            {!sites?.length && <div className="text-sm text-slate-500">No sites available</div>}
          </div>
        </div>

        <div className="flex justify-end space-x-2 pt-4">
          <Button variant="outline" type="button" onClick={() => navigate("/users")}>Cancel</Button>
          <Button type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? "Creating..." : "Create User"}
          </Button>
        </div>
      </form>
    </div>
  );
}
