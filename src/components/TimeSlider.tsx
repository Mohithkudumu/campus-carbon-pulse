import { Slider } from '@/components/ui/slider';
import { Clock } from 'lucide-react';

interface TimeSliderProps {
  value: number;
  onChange: (value: number) => void;
  forecastData?: { hour: number; carbon: number }[];
}

const TimeSlider = ({ value, onChange, forecastData }: TimeSliderProps) => {
  const now = new Date();
  const currentHour = now.getHours();
  
  const formatTime = (hoursFromNow: number): string => {
    const hour = (currentHour + hoursFromNow) % 24;
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:00 ${ampm}`;
  };

  const getLabel = (hoursFromNow: number): string => {
    if (hoursFromNow === 0) return 'Now';
    return `+${hoursFromNow}h`;
  };

  return (
    <div className="glass-panel p-4 w-full max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-primary" />
          <span className="font-display text-xs tracking-wider text-muted-foreground">
            24-HOUR FORECAST
          </span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-muted-foreground">{getLabel(value)}</span>
          <span className="font-display text-sm font-bold text-foreground">
            {formatTime(value)}
          </span>
        </div>
      </div>

      {/* Slider Container */}
      <div className="relative">
        {/* Heat gradient background */}
        <div className="absolute inset-x-0 top-1/2 -translate-y-1/2 h-2 rounded-full heat-bar opacity-30" />
        
        {/* Custom Slider */}
        <Slider
          value={[value]}
          onValueChange={(values) => onChange(values[0])}
          min={0}
          max={24}
          step={1}
          className="relative z-10"
        />
      </div>

      {/* Time Labels */}
      <div className="flex justify-between mt-2 text-[10px] text-muted-foreground">
        <span>Now</span>
        <span>+6h</span>
        <span>+12h</span>
        <span>+18h</span>
        <span>+24h</span>
      </div>
    </div>
  );
};

export default TimeSlider;
