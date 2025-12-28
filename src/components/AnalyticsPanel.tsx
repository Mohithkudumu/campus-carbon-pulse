import { useMemo, useState } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { Activity, Leaf, TrendingUp, TrendingDown, Building2, Clock } from 'lucide-react';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { generateHistoricalData, formatCarbon, getCarbonLevel } from '@/lib/mockData';
import { cn } from '@/lib/utils';

interface AnalyticsPanelProps {
  totalCarbon: number;
  buildingCount: number;
  currentHour: number;
}

const AnalyticsPanel = ({ totalCarbon, buildingCount, currentHour }: AnalyticsPanelProps) => {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '6m'>('7d');

  const historicalData = useMemo(() => {
    const days = timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : 180;
    return generateHistoricalData(days);
  }, [timeRange]);

  const carbonLevel = getCarbonLevel(totalCarbon);
  
  const avgCarbon = useMemo(() => {
    const avg = historicalData.reduce((sum, d) => sum + d.carbon, 0) / historicalData.length;
    return Math.round(avg);
  }, [historicalData]);

  const trend = useMemo(() => {
    if (historicalData.length < 2) return 0;
    const recent = historicalData.slice(-3).reduce((sum, d) => sum + d.carbon, 0) / 3;
    const earlier = historicalData.slice(0, 3).reduce((sum, d) => sum + d.carbon, 0) / 3;
    return ((recent - earlier) / earlier) * 100;
  }, [historicalData]);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="glass-panel p-3 text-xs">
          <p className="font-display text-muted-foreground mb-1">{label}</p>
          <p className="font-bold text-primary">
            {payload[0].value.toLocaleString()} kg CO₂
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="glass-panel p-5 w-80 space-y-5 animate-slide-in">
      {/* Header */}
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
          <Activity className="w-4 h-4 text-primary" />
        </div>
        <div>
          <h2 className="font-display text-sm font-bold tracking-wider">
            CARBON ANALYTICS
          </h2>
          <p className="text-[10px] text-muted-foreground">Real-time monitoring</p>
        </div>
      </div>

      {/* Main Metric */}
      <div className="relative p-4 rounded-xl bg-gradient-to-br from-muted/50 to-transparent border border-border/50">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs text-muted-foreground mb-1">Total Campus Emission</p>
            <div className="flex items-baseline gap-2">
              <span className={cn(
                "font-display text-3xl font-black animate-count-up",
                carbonLevel === 'low' && "text-carbon-low",
                carbonLevel === 'mid' && "text-carbon-mid",
                carbonLevel === 'critical' && "text-carbon-critical"
              )}>
                {formatCarbon(totalCarbon)}
              </span>
              <span className="text-xs text-muted-foreground">kg/h</span>
            </div>
          </div>
          <div className={cn(
            "px-2 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider",
            carbonLevel === 'low' && "bg-carbon-low/20 text-carbon-low",
            carbonLevel === 'mid' && "bg-carbon-mid/20 text-carbon-mid",
            carbonLevel === 'critical' && "bg-carbon-critical/20 text-carbon-critical"
          )}>
            {carbonLevel}
          </div>
        </div>

        {/* Forecast indicator */}
        <div className="mt-3 flex items-center gap-2 text-xs text-muted-foreground">
          <Clock className="w-3 h-3" />
          <span>Forecast: +{currentHour}h from now</span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-3">
        <div className="p-3 rounded-lg bg-muted/30 border border-border/30">
          <div className="flex items-center gap-2 mb-1">
            <Building2 className="w-3 h-3 text-muted-foreground" />
            <span className="text-[10px] text-muted-foreground">Buildings</span>
          </div>
          <p className="font-display text-lg font-bold">{buildingCount}</p>
        </div>
        
        <div className="p-3 rounded-lg bg-muted/30 border border-border/30">
          <div className="flex items-center gap-2 mb-1">
            {trend >= 0 ? (
              <TrendingUp className="w-3 h-3 text-carbon-critical" />
            ) : (
              <TrendingDown className="w-3 h-3 text-carbon-low" />
            )}
            <span className="text-[10px] text-muted-foreground">Trend</span>
          </div>
          <p className={cn(
            "font-display text-lg font-bold",
            trend >= 0 ? "text-carbon-critical" : "text-carbon-low"
          )}>
            {trend >= 0 ? '+' : ''}{trend.toFixed(1)}%
          </p>
        </div>
      </div>

      {/* Chart Section */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Leaf className="w-3 h-3 text-primary" />
            <span className="text-xs font-medium">Historical Data</span>
          </div>
          <Tabs value={timeRange} onValueChange={(v) => setTimeRange(v as any)}>
            <TabsList className="h-7 p-0.5 bg-muted/50">
              <TabsTrigger value="7d" className="text-[10px] h-6 px-2">7D</TabsTrigger>
              <TabsTrigger value="30d" className="text-[10px] h-6 px-2">30D</TabsTrigger>
              <TabsTrigger value="6m" className="text-[10px] h-6 px-2">6M</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        <div className="h-32 -mx-2">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={historicalData}>
              <defs>
                <linearGradient id="carbonGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="hsl(145, 100%, 45%)" stopOpacity={0.4} />
                  <stop offset="50%" stopColor="hsl(51, 100%, 50%)" stopOpacity={0.2} />
                  <stop offset="100%" stopColor="hsl(351, 100%, 55%)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(0, 0%, 20%)" />
              <XAxis 
                dataKey="date" 
                tick={{ fontSize: 9, fill: 'hsl(0, 0%, 60%)' }}
                tickLine={false}
                axisLine={false}
                interval={timeRange === '7d' ? 0 : 'preserveStartEnd'}
              />
              <YAxis 
                tick={{ fontSize: 9, fill: 'hsl(0, 0%, 60%)' }}
                tickLine={false}
                axisLine={false}
                width={35}
                tickFormatter={(v) => `${(v/1000).toFixed(1)}k`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="carbon"
                stroke="hsl(145, 100%, 45%)"
                strokeWidth={2}
                fill="url(#carbonGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="flex justify-between mt-2 text-[10px] text-muted-foreground">
          <span>Avg: {avgCarbon.toLocaleString()} kg/h</span>
          <span>Peak: {Math.max(...historicalData.map(d => d.carbon)).toLocaleString()} kg/h</span>
        </div>
      </div>

      {/* Legend */}
      <div className="pt-3 border-t border-border/30">
        <p className="text-[10px] text-muted-foreground mb-2">Emission Levels</p>
        <div className="heat-bar h-2 rounded-full" />
        <div className="flex justify-between mt-1 text-[10px]">
          <span className="text-carbon-low">Low</span>
          <span className="text-carbon-mid">Mid</span>
          <span className="text-carbon-critical">Critical</span>
        </div>
      </div>
    </div>
  );
};


export default AnalyticsPanel;
