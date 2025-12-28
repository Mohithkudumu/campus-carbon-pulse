import { Zap } from 'lucide-react';

const DashboardHeader = () => {
  return (
    <div className="glass-panel p-4 pl-6 animate-fade-in">
      <div className="flex items-center gap-4">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center animate-pulse-glow">
          <Zap className="w-5 h-5 text-primary-foreground" />
        </div>
        <div>
          <h1 className="font-display text-xl font-black tracking-wider cyber-text">
            CAMPUS TWIN
          </h1>
          <p className="text-[11px] text-muted-foreground tracking-wide">
            Digital Carbon Footprint Monitor
          </p>
        </div>
      </div>

      {/* Status Indicator */}
      <div className="flex items-center gap-2 mt-3 pt-3 border-t border-border/30">
        <div className="w-2 h-2 rounded-full bg-carbon-low animate-pulse" />
        <span className="text-[10px] text-muted-foreground">System Online</span>
        <span className="text-[10px] text-muted-foreground ml-auto">
          Last sync: Just now
        </span>
      </div>
    </div>
  );
};

export default DashboardHeader;
