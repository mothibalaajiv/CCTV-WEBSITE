import { useQuery } from "@tanstack/react-query";
import api from "../../lib/api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../components/ui/table";

export default function CameraHistory() {
  const { data: history, isLoading } = useQuery({
    queryKey: ["camera-history"],
    queryFn: () => api.get("/system/camera-history").then((res) => res.data),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Camera Movement History</h1>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Camera Code</TableHead>
              <TableHead>Old Site</TableHead>
              <TableHead>New Site</TableHead>
              <TableHead>Moved At</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow><TableCell colSpan={4} className="text-center">Loading...</TableCell></TableRow>
            ) : history?.length ? (
              history.map((record) => (
                <TableRow key={record._id}>
                  <TableCell className="font-medium">{record.camera_code}</TableCell>
                  <TableCell>{record.old_site}</TableCell>
                  <TableCell>{record.new_site}</TableCell>
                  <TableCell>{new Date(record.moved_at).toLocaleString()}</TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow><TableCell colSpan={4} className="text-center">No history found.</TableCell></TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
