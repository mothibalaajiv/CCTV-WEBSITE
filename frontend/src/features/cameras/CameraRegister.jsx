import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../../lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "../../components/ui/card";
import { Input } from "../../components/ui/input";
import { Button } from "../../components/ui/button";

export default function CameraRegister() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    mac_address: ""
  });

  const mutation = useMutation({
    mutationFn: (data) => api.post("/cameras", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cameras"] });
      navigate("/cameras");
    },
    onError: (err) => {
      alert(err.response?.data?.message || "Error registering camera");
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  return (
    <div className="max-w-xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Register Camera</h1>
      </div>
      
      <Card>
        <form onSubmit={handleSubmit}>
          <CardHeader>
            <CardTitle>Camera Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">MAC Address</label>
              <Input 
                required 
                placeholder="00:1A:79:11:22:33"
                value={formData.mac_address}
                onChange={e => setFormData({...formData, mac_address: e.target.value})}
              />
            </div>
          </CardContent>
          <CardFooter className="flex justify-end gap-2">
            <Button variant="outline" type="button" onClick={() => navigate("/cameras")}>Cancel</Button>
            <Button type="submit">Register</Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
