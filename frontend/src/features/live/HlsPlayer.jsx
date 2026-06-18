import { useEffect, useRef } from 'react';
import Hls from 'hls.js';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Pause, Play } from 'lucide-react';

export default function HlsPlayer({ url, title, status, isAdmin, onPause, onResume, isPending }) {
  const videoRef = useRef(null);

  useEffect(() => {
    let hls;
    if (videoRef.current && status === 'active') {
      if (Hls.isSupported()) {
        hls = new Hls();
        hls.loadSource(url);
        hls.attachMedia(videoRef.current);
        hls.on(Hls.Events.MANIFEST_PARSED, () => {
          videoRef.current.play().catch(e => console.log("Auto-play prevented", e));
        });
      } else if (videoRef.current.canPlayType('application/vnd.apple.mpegurl')) {
        // For Safari
        videoRef.current.src = url;
        videoRef.current.addEventListener('loadedmetadata', () => {
          videoRef.current.play().catch(e => console.log("Auto-play prevented", e));
        });
      }
    }

    return () => {
      if (hls) {
        hls.destroy();
      }
    };
  }, [url, status]);

  return (
    <Card className="overflow-hidden bg-black text-white">
      <CardHeader className="p-3 bg-secondary/80">
        <CardTitle className="text-sm flex justify-between items-center">
          <div>{title}</div>
          <div className="flex items-center gap-2">
            {isAdmin && status === 'active' && (
              <Button size="icon" variant="ghost" className="h-6 w-6 text-white hover:bg-white/20 hover:text-white" onClick={onPause} disabled={isPending}>
                <Pause className="h-4 w-4" />
              </Button>
            )}
            {isAdmin && status === 'paused' && (
              <Button size="icon" variant="ghost" className="h-6 w-6 text-white hover:bg-white/20 hover:text-white" onClick={onResume} disabled={isPending}>
                <Play className="h-4 w-4" />
              </Button>
            )}
            <span className={`w-2 h-2 rounded-full ${status === 'active' ? 'bg-green-500' : 'bg-red-500'}`} title={status}></span>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0 relative aspect-video bg-black flex items-center justify-center">
        {status === 'active' ? (
          <video
            ref={videoRef}
            className="w-full h-full object-cover"
            controls
            muted
            playsInline
          />
        ) : (
          <div className="text-muted-foreground text-sm flex flex-col items-center">
            <span>Stream Paused / Offline</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
