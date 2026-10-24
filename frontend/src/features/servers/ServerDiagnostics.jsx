import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "../../lib/api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../components/ui/table";
import { Button } from "../../components/ui/button";
import { 
  Activity, Server, Camera, AlertTriangle, CheckCircle2, XCircle, 
  RefreshCw, HardDrive, Cpu, Clock, ShieldAlert, Wifi, Video, Tag, FileText,
  Cloud, UploadCloud, Power, Monitor
} from "lucide-react";

export default function ServerDiagnostics() {
  const { data: diagnostics, isLoading, isError, error, refetch, isRefetching } = useQuery({
    queryKey: ["server-diagnostics"],
    queryFn: () => api.get("/servers/diagnostics").then((res) => res.data),
    refetchInterval: 15000,
  });

  const effectiveDiagnostics = diagnostics || [];

  if (isLoading && !isRefetching && !diagnostics) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400">
        <RefreshCw className="h-6 w-6 animate-spin mr-3" />
        Loading diagnostic telemetry...
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-slate-400 border border-rose-500/20 bg-rose-500/5 rounded-xl">
        <ShieldAlert className="h-10 w-10 text-rose-500 mb-4" />
        <h3 className="text-lg font-semibold text-rose-400 mb-2">Telemetry Pipeline Error</h3>
        <p className="text-sm text-slate-400 mb-4 text-center max-w-md">
          Failed to fetch real-time diagnostics from the server. <br/>
          {error?.message || "Unknown network error"}
        </p>
        <Button 
          onClick={() => refetch()} 
          disabled={isRefetching}
          className="bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${isRefetching ? "animate-spin" : ""}`} />
          {isRefetching ? "Retrying..." : "Retry Connection"}
        </Button>
      </div>
    );
  }

  const formatUptime = (seconds) => {
    if (!seconds || seconds <= 0) return "0m";
    const d = Math.floor(seconds / (3600 * 24));
    const h = Math.floor((seconds % (3600 * 24)) / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    if (d > 0) return `${d}d ${h}h ${m}m`;
    if (h > 0) return `${h}h ${m}m`;
    if (m > 0) return `${m}m ${s}s`;
    return `${s}s`;
  };

  const getCurrentFootageName = (cam) => {
    if (cam.current_footage_name) return cam.current_footage_name;
    const loc = (cam.location_name || "tbi_front_gate").trim().toLowerCase().replace(/\s+/g, "_");
    const now = new Date();
    const pad = (n) => String(n).padStart(2, "0");
    const dateStr = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
    const minBlock = Math.floor(now.getMinutes() / 15) * 15;
    const timeStr = `${pad(now.getHours())}-${pad(minBlock)}-00`;
    return `${loc}_${dateStr}_${timeStr}.mp4`;
  };

  const getStatusBadge = (status, text) => {
    const norm = typeof status === "string" ? status.toLowerCase() : status;
    if (norm === "active" || norm === "online" || norm === true) {
      return (
        <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-semibold text-emerald-400 border border-emerald-500/20">
          <CheckCircle2 className="h-3 w-3" />
          {text || "Active"}
        </span>
      );
    }
    if (norm === "error" || norm === "offline" || norm === false) {
      return (
        <span className="inline-flex items-center gap-1.5 rounded-full bg-rose-500/10 px-2.5 py-1 text-xs font-semibold text-rose-400 border border-rose-500/20">
          <XCircle className="h-3 w-3" />
          {text || "Offline"}
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-500/10 px-2.5 py-1 text-xs font-semibold text-amber-400 border border-amber-500/20">
        <Activity className="h-3 w-3" />
        {text || status || "Stopped"}
      </span>
    );
  };

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-primary/10 text-primary border border-primary/20">
              <Activity className="h-6 w-6 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white">System Troubleshooting & Diagnostics</h1>
              <p className="text-sm text-slate-400">Real-time telemetry, hardware health, and stream error analysis</p>
            </div>
          </div>
        </div>
        <Button 
          onClick={() => refetch()} 
          disabled={isRefetching}
          className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700"
        >
          <RefreshCw className={`h-4 w-4 ${isRefetching ? "animate-spin" : ""}`} />
          {isRefetching ? "Refreshing..." : "Refresh Live Data"}
        </Button>
      </div>

      {effectiveDiagnostics.map((server) => (
          <div key={server._id} className="rounded-xl border border-slate-800 bg-slate-900/60 shadow-xl overflow-hidden backdrop-blur-sm transition-all hover:border-slate-700/80">
            {/* Server Header Bar */}
            <div className="bg-slate-900/90 border-b border-slate-800 p-6 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
              <div className="flex items-center gap-4">
                <div className={`p-3 rounded-xl border ${String(server.status).toLowerCase() === "online" ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400" : "bg-rose-500/10 border-rose-500/30 text-rose-400"}`}>
                  <Server className="h-6 w-6" />
                </div>
                <div>
                  <div className="flex flex-wrap items-center gap-2.5">
                    <h2 className="text-lg font-bold text-white">Server {server.server_id}</h2>
                    
                    {/* PC Power / Physical Machine Status */}
                    <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${String(server.status).toLowerCase() === "online" ? "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30" : "bg-rose-500/15 text-rose-300 border border-rose-500/30"}`}>
                      <Power className="h-3.5 w-3.5 shrink-0" />
                      <span>PC Status: {String(server.status).toLowerCase() === "online" ? "POWER ON" : "POWER OFF"}</span>
                    </div>

                    {/* VMS Local Server Application Status */}
                    <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${String(server.agent_status).toLowerCase() === "active" ? "bg-sky-500/15 text-sky-300 border border-sky-500/30" : "bg-rose-500/15 text-rose-300 border border-rose-500/30"}`}>
                      <Activity className={`h-3.5 w-3.5 shrink-0 ${String(server.agent_status).toLowerCase() === "active" ? "text-sky-400" : "text-rose-400"}`} />
                      <span>Local Server Agent: {String(server.agent_status || "active").toUpperCase()}</span>
                    </div>

                    {/* Cloud to Local Server Communication Link */}
                    <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${String(server.status).toLowerCase() === "online" ? "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30" : "bg-amber-500/15 text-amber-300 border border-amber-500/30"}`}>
                      <Wifi className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
                      <span>Cloud ⇄ Local Comm: {String(server.status).toLowerCase() === "online" ? "CONNECTED" : "DISCONNECTED"}</span>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400 mt-1.5">
                    <span>Host: <strong className="text-slate-300">{server.hostname}</strong></span>
                    <span>•</span>
                    <span>IP: <strong className="text-slate-300">{server.ip_address}</strong></span>
                    <span>•</span>
                    <span>MAC: <strong className="text-slate-300 font-mono">{server.mac_address}</strong></span>
                  </div>

                  <div className="flex flex-wrap items-center gap-4 mt-2.5 pt-2 border-t border-slate-800/80 text-xs">
                    <div className="flex items-center gap-2">
                      <Monitor className="h-4 w-4 text-emerald-400" />
                      <span className="text-slate-400">Host Machine (PC):</span>
                      <span className={`font-semibold px-2 py-0.5 rounded ${String(server.status).toLowerCase() === "online" ? "bg-emerald-500/10 text-emerald-300 border border-emerald-500/20" : "bg-rose-500/10 text-rose-300 border border-rose-500/20"}`}>
                        {String(server.status).toLowerCase() === "online" ? "POWER ON & NETWORK REACHABLE" : "POWER OFF / UNREACHABLE"}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Server className={`h-4 w-4 ${String(server.agent_status).toLowerCase() === "active" ? "text-sky-400" : "text-rose-400"}`} />
                      <span className="text-slate-400">VMS Agent App (`CCTV-Agent.exe`):</span>
                      <span className={`font-semibold px-2 py-0.5 rounded ${String(server.agent_status).toLowerCase() === "active" ? "bg-sky-500/10 text-sky-300 border border-sky-500/20" : "bg-rose-500/10 text-rose-300 border border-rose-500/20"}`}>
                        {String(server.agent_status).toLowerCase() === "active" ? "RUNNING (ACTIVE TELEMETRY)" : "STOPPED / OFFLINE"}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Wifi className="h-4 w-4 text-emerald-400" />
                      <span className="text-slate-400">Cloud &rarr; Local Comm:</span>
                      <span className={`font-semibold px-2 py-0.5 rounded ${String(server.status).toLowerCase() === "online" ? "bg-emerald-500/10 text-emerald-300 border border-emerald-500/20" : "bg-rose-500/10 text-rose-300 border border-rose-500/20"}`}>
                        {String(server.status).toLowerCase() === "online" ? "COMMAND & HEARTBEAT SYNC ACTIVE" : "DISCONNECTED"}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Hardware Telemetry Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 bg-slate-950/60 p-3.5 rounded-lg border border-slate-800/80 text-xs">
                <div className="flex items-center gap-3 px-2 border-r border-slate-800/60 last:border-0">
                  <Cpu className="h-4 w-4 text-sky-400 shrink-0" />
                  <div>
                    <div className="text-slate-400">CPU Load</div>
                    <div className={`font-bold mt-0.5 ${server.cpu_usage_percent > 80 ? "text-rose-400" : "text-slate-200"}`}>
                      {server.cpu_usage_percent}%
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3 px-2 border-r border-slate-800/60 last:border-0">
                  <Activity className="h-4 w-4 text-violet-400 shrink-0" />
                  <div>
                    <div className="text-slate-400">Memory Usage</div>
                    <div className={`font-bold mt-0.5 ${server.memory_usage_percent > 85 ? "text-rose-400" : "text-slate-200"}`}>
                      {server.memory_usage_percent}%
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3 px-2 border-r border-slate-800/60 last:border-0">
                  <HardDrive className="h-4 w-4 text-emerald-400 shrink-0" />
                  <div>
                    <div className="text-slate-400">Disk Free</div>
                    <div className="font-bold text-slate-200 mt-0.5">
                      {server.disk_free_gb} GB <span className="text-[10px] text-slate-500">/ {server.disk_total_gb} GB</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3 px-2">
                  <Clock className="h-4 w-4 text-amber-400 shrink-0" />
                  <div>
                    <div className="text-slate-400">Uptime</div>
                    <div className="font-bold text-slate-200 mt-0.5">
                      {formatUptime(server.uptime_seconds)}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Cameras Troubleshooting Section */}
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                  <Camera className="h-4 w-4 text-primary" />
                  Local Server {server.server_id} — Assigned Camera Recording Status ({server.cameras?.length || 0})
                </h3>
                <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400">
                  <span className="flex items-center gap-1"><Video className="h-3.5 w-3.5 text-emerald-400" /> Active Rec: <strong className="text-slate-200">{server.active_recordings_count}</strong></span>
                  <span>•</span>
                  <span className="flex items-center gap-1"><Tag className="h-3.5 w-3.5 text-purple-400" /> Name Assigned: <strong className="text-slate-200">{server.cameras?.filter(c => c.footage_name_status === "assigned" || c.footage_name_assigned !== false).length || 0}/{server.cameras?.length || 0}</strong></span>
                  <span>•</span>
                  <span className="flex items-center gap-1"><Activity className="h-3.5 w-3.5 text-sky-400" /> Cloud Streams: <strong className="text-slate-200">{server.active_cloud_streams_count}</strong></span>
                  <span>•</span>
                  <span>FFmpeg Workers: <strong className="text-slate-200">{server.ffmpeg_process_count}</strong></span>
                </div>
              </div>

              {!server.cameras || server.cameras.length === 0 ? (
                <div className="rounded-lg border border-slate-800/80 bg-slate-950/30 p-8 text-center text-sm text-slate-500">
                  No cameras currently detected or reporting diagnostics on this server.
                </div>
              ) : (
                <div className="rounded-lg border border-slate-800/80 overflow-hidden">
                  <Table>
                    <TableHeader className="bg-slate-950/80">
                      <TableRow className="border-slate-800 hover:bg-transparent">
                        <TableHead className="text-slate-400 font-semibold">Camera</TableHead>
                        <TableHead className="text-slate-400 font-semibold">Network & RTSP</TableHead>
                        <TableHead className="text-slate-400 font-semibold">Local Recording</TableHead>
                        <TableHead className="text-slate-400 font-semibold">Footage Name Assignment</TableHead>
                        <TableHead className="text-slate-400 font-semibold">Footage Push to Cloud Status</TableHead>
                        <TableHead className="text-slate-400 font-semibold">Diagnostic Status & Logs</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {server.cameras.map((cam, idx) => (
                        <TableRow key={cam.camera_mac || idx} className="border-slate-800/60 hover:bg-slate-800/30 transition-colors">
                          <TableCell>
                            <div className="font-semibold text-slate-200">{cam.camera_code || "Unregistered"}</div>
                            <div className="text-xs text-slate-400">{cam.location_name || "Unknown Location"}</div>
                            <div className="text-[10px] font-mono text-slate-500 mt-0.5">{cam.camera_mac} ({cam.camera_ip})</div>
                          </TableCell>

                          <TableCell>
                            <div className="flex flex-col gap-1.5 items-start">
                              {getStatusBadge(cam.ping_status, cam.ping_status === 'online' ? "Network Reachable" : "Network Unreachable")}
                              {getStatusBadge(cam.rtsp_reachable, cam.rtsp_reachable ? "RTSP Validated" : "RTSP Error")}
                            </div>
                          </TableCell>

                          <TableCell>
                            <div className="flex flex-col gap-1.5 items-start">
                              {getStatusBadge(cam.recording_status, String(cam.recording_status).toLowerCase() === "active" ? "Recording Active" : "Stopped")}
                              <div className="flex flex-col gap-0.5 text-[11px] text-slate-400">
                                <span className="flex items-center gap-1 text-slate-300 font-medium">
                                  <HardDrive className="h-3 w-3 text-emerald-400 shrink-0" />
                                  Server {server.server_id} Storage
                                </span>
                                <span className="text-[10px] text-slate-500 font-mono">15-Min Segment Rotation</span>
                              </div>
                            </div>
                          </TableCell>

                          <TableCell>
                            <div className="flex flex-col gap-1.5 items-start">
                              {(cam.footage_name_status === "assigned" || cam.footage_name_assigned !== false) ? (
                                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 shrink-0" /> Assigned (15m window)
                                </span>
                              ) : (
                                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30">
                                  <AlertTriangle className="h-3.5 w-3.5 text-amber-400 shrink-0" /> Not Assigned
                                </span>
                              )}
                              <div className="flex flex-col gap-0.5 mt-0.5">
                                <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Current Active Footage File:</span>
                                <div className="text-xs font-mono text-emerald-400 bg-slate-950/90 px-2.5 py-1 rounded-md border border-slate-800 flex items-center gap-1.5 shadow-sm">
                                  <FileText className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
                                  <span className="truncate max-w-[240px]" title={getCurrentFootageName(cam)}>
                                    {getCurrentFootageName(cam)}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </TableCell>

                          <TableCell>
                            <div className="flex flex-col gap-1.5 items-start">
                              {getStatusBadge(
                                cam.cloud_push_status,
                                String(cam.cloud_push_status).toLowerCase() === "active"
                                  ? "Cloud Push Active"
                                  : "Push Stopped"
                              )}
                              <div className="flex flex-col gap-1 text-[11px] text-slate-400 mt-0.5">
                                <div className="flex items-center gap-1.5 text-slate-300 font-medium">
                                  <Cloud className="h-3.5 w-3.5 text-sky-400 shrink-0" />
                                  <span>Server {server.server_id} &rarr; Cloud (104.251.214.177)</span>
                                </div>
                              </div>
                            </div>
                          </TableCell>

                          <TableCell>
                            {cam.error_message ? (
                              <div className="flex items-start gap-2 p-2.5 rounded-md bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs max-w-md">
                                <AlertTriangle className="h-4 w-4 text-rose-400 shrink-0 mt-0.5" />
                                <div>
                                  <div className="font-semibold">Stream Error Detected:</div>
                                  <div className="text-rose-200/90 mt-0.5">{cam.error_message}</div>
                                </div>
                              </div>
                            ) : (
                              <div className="flex items-center gap-2 text-xs text-emerald-400 bg-emerald-500/5 px-3 py-2 rounded-md border border-emerald-500/10 w-fit">
                                <CheckCircle2 className="h-4 w-4" />
                                <span>All stream parameters operating normally</span>
                              </div>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </div>
          </div>
        ))}
    </div>
  );
}
