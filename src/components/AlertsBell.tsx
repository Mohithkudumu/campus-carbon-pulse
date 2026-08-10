import { useState, useEffect } from 'react';
import { Bell, AlertTriangle, CheckCheck, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { Popover, PopoverTrigger, PopoverContent } from '@/components/ui/popover';

export interface CarbonAlert {
  id: number;
  building_id: string;
  timestamp: string;
  emission: number;
  limit_value: number;
  alert_msg: string;
  severity: string;
}

const AlertsBell = () => {
  const [alerts, setAlerts] = useState<CarbonAlert[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchAlerts = async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/get-alerts');
      if (res.ok) {
        const data = await res.json();
        setAlerts(data);
      }
    } catch (err) {
      console.error('Failed to fetch alerts:', err);
    } finally {
      if (!silent) setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchAlerts();

    // Poll every 10 seconds for new alerts
    const interval = setInterval(() => {
      fetchAlerts(true);
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  const handleResolveAlert = async (id: number) => {
    try {
      const res = await fetch(`http://localhost:8000/resolve-alert/${id}`, {
        method: 'POST',
      });
      if (res.ok) {
        toast.success(`Alert resolved successfully`);
        // Remove from list
        setAlerts((prev) => prev.filter((alert) => alert.id !== id));
      } else {
        toast.error('Failed to resolve alert');
      }
    } catch (err) {
      console.error('Error resolving alert:', err);
      toast.error('Error connecting to backend');
    }
  };

  // Sort alerts so CRITICAL ones are first
  const sortedAlerts = [...alerts].sort((a, b) => {
    if (a.severity === 'CRITICAL' && b.severity !== 'CRITICAL') return -1;
    if (a.severity !== 'CRITICAL' && b.severity === 'CRITICAL') return 1;
    return 0;
  });

  return (
    <div className="relative inline-block text-left animate-fade-in shadow-xl">
      <Popover>
        <PopoverTrigger asChild>
          <button
            className={`flex items-center justify-center p-3 rounded-lg border transition-all duration-300 relative ${alerts.length > 0
              ? 'border-red-500 bg-[#450a0a] hover:bg-[#7f1d1d] text-red-200 hover:scale-105 shadow-[0_0_15px_rgba(239,68,68,0.3)]'
              : 'border-border/80 bg-[#0F172A] hover:bg-[#1E293B] text-muted-foreground hover:text-foreground'
              }`}
            title="Active Carbon Alerts"
          >
            <Bell className={`w-5 h-5 ${alerts.length > 0 ? 'animate-[bounce_1.5s_infinite]' : ''}`} />

            {alerts.length > 0 && (
              <span className="absolute -top-1.5 -right-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-red-600 text-[10px] font-bold text-white ring-2 ring-black animate-pulse">
                {alerts.length}
              </span>
            )}
          </button>
        </PopoverTrigger>

        <PopoverContent
          align="end"
          sideOffset={8}
          className="w-80 max-h-96 z-50 overflow-y-auto bg-[#0B0F19] border border-border p-4 rounded-xl shadow-2xl flex flex-col gap-3"
        >
          <div className="flex items-center justify-between border-b border-border pb-2">
            <h3 className="font-display font-bold text-sm text-foreground flex items-center gap-1.5">
              <AlertTriangle className="w-4 h-4 text-amber-500" />
              Active System Warnings
            </h3>
            {loading && <Loader2 className="w-3.5 h-3.5 animate-spin text-muted-foreground" />}
            {!loading && (
              <span className="text-[10px] text-muted-foreground px-2 py-0.5 rounded-full bg-[#1E293B] border border-border">
                {alerts.length} Warnings
              </span>
            )}
          </div>

          <div className="flex flex-col gap-2 overflow-y-auto max-h-[260px] pr-1">
            {alerts.length === 0 ? (
              <div className="text-center py-6 text-xs text-muted-foreground flex flex-col items-center gap-2">
                <CheckCheck className="w-8 h-8 text-green-500/60" />
                <span>All building emissions within safe margins.</span>
              </div>
            ) : (
              sortedAlerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`p-3 rounded-lg border flex flex-col gap-1.5 transition-all text-[11px] ${alert.severity === 'CRITICAL'
                    ? 'border-red-500 bg-[#450a0a]/40 text-red-200 shadow-[inset_0_0_10px_rgba(239,68,68,0.1)]'
                    : 'border-amber-500 bg-[#78350f]/40 text-amber-200 shadow-[inset_0_0_10px_rgba(245,158,11,0.1)]'
                    }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold uppercase tracking-wider">{alert.building_id.replace(/_/g, ' ')}</span>
                    <span
                      className={`px-1.5 py-0.5 rounded font-mono text-[9px] font-bold ${alert.severity === 'CRITICAL' ? 'bg-red-500/35 text-red-200 font-black' : 'bg-amber-500/35 text-amber-200'
                        }`}
                    >
                      {alert.severity}
                    </span>
                  </div>
                  <p className="text-muted-foreground text-[10px] leading-relaxed">{alert.alert_msg}</p>
                  <div className="flex items-center justify-between mt-1 pt-1.5 border-t border-white/5 text-[9px]">
                    <span className="text-muted-foreground font-mono">
                      {new Date(alert.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                    <button
                      onClick={() => handleResolveAlert(alert.id)}
                      className="px-2 py-1 bg-primary hover:bg-primary/80 text-primary-foreground font-semibold rounded transition duration-200 flex items-center gap-1"
                    >
                      Resolve
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </PopoverContent>
      </Popover>
    </div>
  );
};

export default AlertsBell;
