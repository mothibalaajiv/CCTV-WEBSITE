import { useEffect, useRef, useState } from 'react';
import Hls from 'hls.js';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Pause, Play, AlertCircle, Loader2 } from 'lucide-react';

export default function HlsPlayer({ url, title, status, isAdmin, onPause, onResume, isPending }) {
  const videoRef = useRef(null);
  const [hasSignal, setHasSignal] = useState(true);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let hls;
    let timeoutId;
    setHasSignal(true);
    setIsLoading(true);

    if (videoRef.current && status === 'active') {
      // Set a 5-second timer. If manifest/fragments don't load by then, declare No Signal.
      timeoutId = setTimeout(() => {
        setHasSignal(false);
        setIsLoading(false);
        if (hls) hls.destroy();
      }, 5000);

      if (Hls.isSupported()) {
        hls = new Hls({
          manifestLoadingTimeOut: 4000,
          manifestLoadingMaxRetry: 1,
          levelLoadingTimeOut: 4000,
          levelLoadingMaxRetry: 1,
        });
        hls.loadSource(url);
        hls.attachMedia(videoRef.current);
        
        hls.on(Hls.Events.MANIFEST_PARSED, () => {
          clearTimeout(timeoutId);
          setHasSignal(true);
          setIsLoading(false);
          videoRef.current.play().catch(e => console.log("Auto-play prevented", e));
        });

        hls.on(Hls.Events.FRAG_LOADED, () => {
          clearTimeout(timeoutId);
          setHasSignal(true);
          setIsLoading(false);
        });

        hls.on(Hls.Events.ERROR, (event, data) => {
          if (data.fatal || data.type === Hls.ErrorTypes.NETWORK_ERROR) {
            console.log("HLS error encountered:", data.type);
            clearTimeout(timeoutId);
            setHasSignal(false);
            setIsLoading(false);
            if (hls) hls.destroy();
          }
        });
      } else if (videoRef.current.canPlayType('application/vnd.apple.mpegurl')) {
        // For Safari
        videoRef.current.src = url;
        videoRef.current.addEventListener('loadedmetadata', () => {
          clearTimeout(timeoutId);
          setHasSignal(true);
          setIsLoading(false);
          videoRef.current.play().catch(e => console.log("Auto-play prevented", e));
        });
        videoRef.current.addEventListener('error', () => {
          clearTimeout(timeoutId);
          setHasSignal(false);
          setIsLoading(false);
        });
      }
    } else {
      setIsLoading(false);
    }

    return () => {
      clearTimeout(timeoutId);
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
            <span className={`w-2 h-2 rounded-full ${status === 'active' && hasSignal && !isLoading ? 'bg-green-500' : 'bg-red-500'}`} title={status}></span>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0 relative aspect-video bg-neutral-950 flex items-center justify-center">
        {status === 'active' ? (
          <>
            <video
              ref={videoRef}
              className={`w-full h-full object-cover ${(!hasSignal || isLoading) ? 'hidden' : ''}`}
              controls
              muted
              playsInline
            />
            {isLoading && hasSignal && (
              <div className="absolute inset-0 bg-neutral-950 flex flex-col items-center justify-center text-neutral-400 gap-2 z-10">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
                <span className="text-sm font-medium text-white">Connecting to Stream...</span>
              </div>
            )}
            {!hasSignal && !isLoading && (
              <div className="absolute inset-0 bg-neutral-950 flex flex-col items-center justify-center text-neutral-400 gap-2 z-10">
                <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center text-red-500 mb-1">
                  <AlertCircle className="w-6 h-6" />
                </div>
                <span className="font-semibold text-white">No Video Signal</span>
                <span className="text-xs text-neutral-500">Camera is currently not streaming</span>
              </div>
            )}
          </>
        ) : (
          <div className="text-muted-foreground text-sm flex flex-col items-center">
            <span>Stream Paused / Offline</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
