import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import api from "../../lib/api";
import HlsPlayer from "./HlsPlayer";
import { useAuth } from "../../hooks/useAuth";
import { Pencil, Check, X } from "lucide-react";

const EditableTitle = ({ camera, updateCameraMutation, fallbackName }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [value, setValue] = useState(camera?.location_name || "");

  if (!camera) return <span>{fallbackName}</span>;

  const handleSave = () => {
    if (value.trim()) {
      updateCameraMutation.mutate({ id: camera._id, data: { location_name: value } });
    }
    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <div className="flex items-center gap-2" onClick={e => e.stopPropagation()}>
        <input 
          className="border rounded px-1 text-black text-xs"
          value={value} 
          onChange={e => setValue(e.target.value)} 
          onKeyDown={e => e.key === 'Enter' && handleSave()}
          autoFocus 
        />
        <Check className="h-4 w-4 cursor-pointer text-green-500 hover:text-green-400" onClick={handleSave} />
        <X className="h-4 w-4 cursor-pointer text-red-500 hover:text-red-400" onClick={() => { setIsEditing(false); setValue(camera.location_name); }} />
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 group">
      <span>{camera.location_name} ({camera.camera_code})</span>
      <Pencil 
        className="h-3 w-3 cursor-pointer text-transparent group-hover:text-gray-300 transition-colors" 
        onClick={() => setIsEditing(true)} 
      />
    </div>
  );
};

export default function LiveStreams() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";

  const { data: streams, isLoading: isLoadingStreams } = useQuery({
    queryKey: ["streams"],
    queryFn: () => api.get("/streams").then((res) => res.data),
  });

  const { data: cameras, isLoading: isLoadingCameras } = useQuery({
    queryKey: ["cameras"],
    queryFn: () => api.get("/cameras").then((res) => res.data),
  });

  const { data: servers } = useQuery({
    queryKey: ["servers"],
    queryFn: () => api.get("/servers").then(res => res.data)
  });

  const { data: sites } = useQuery({
    queryKey: ["sites"],
    queryFn: () => api.get("/sites").then(res => res.data)
  });

  const pauseMutation = useMutation({
    mutationFn: (camera_code) => api.post("/streams/pause", { camera_code }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["streams"] }),
  });

  const resumeMutation = useMutation({
    mutationFn: (camera_code) => api.post("/streams/resume", { camera_code }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["streams"] }),
  });

  const updateCameraMutation = useMutation({
    mutationFn: ({ id, data }) => api.put(`/cameras/${id}`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["cameras"] })
  });

  if (isLoadingStreams || isLoadingCameras) return <div>Loading streams...</div>;

  // Group streams by Local Server MAC -> Site
  const groupedStreams = {};
  streams?.forEach(stream => {
    const camera = cameras?.find(c => c.camera_code === stream.camera_code);
    let siteName = "Unassigned / Unknown Site";

    // 1. Try grouping by local_server_mac (if stream payload provides it)
    if (stream.local_server_mac) {
      const server = servers?.find(s => s.mac_address === stream.local_server_mac);
      if (server) {
        const site = sites?.find(s => s.local_server_id === server.server_id);
        if (site) siteName = `${site.site_name} (Site ${site.site_id})`;
      }
    } 
    // 2. Fallback: use camera's current_site for now if stream doesn't have local_server_mac
    else if (camera?.current_site) {
      const site = sites?.find(s => s.site_id === camera.current_site);
      if (site) siteName = `${site.site_name} (Site ${site.site_id})`;
    }

    if (!groupedStreams[siteName]) groupedStreams[siteName] = [];
    groupedStreams[siteName].push({ stream, camera });
  });

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Live Streams</h1>
      {Object.keys(groupedStreams).map(site => (
        <div key={site} className="space-y-4">
          <h2 className="text-2xl font-semibold border-b pb-2">{site}</h2>
          <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
            {groupedStreams[site].map(({ stream, camera }) => {
              return (
                <HlsPlayer 
                  key={stream._id} 
                  url={stream.hls_url} 
                  title={
                    <EditableTitle 
                      camera={camera} 
                      updateCameraMutation={updateCameraMutation} 
                      fallbackName={stream.camera_code}
                    />
                  } 
                  status={stream.status}
                  isAdmin={isAdmin}
                  onPause={() => pauseMutation.mutate(stream.camera_code)}
                  onResume={() => resumeMutation.mutate(stream.camera_code)}
                  isPending={pauseMutation.isPending || resumeMutation.isPending}
                />
              );
            })}
          </div>
        </div>
      ))}
      {streams?.length === 0 && <p>No active streams available.</p>}
    </div>
  );
}
