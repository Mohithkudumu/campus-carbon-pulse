import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Sparkles, Loader2, AlertCircle, Clock, Building2, TrendingUp, Lightbulb } from 'lucide-react';
import InsightCard from '@/components/InsightCard';

interface InsightItem {
  title: string;
  description: string;
  value?: string;
  impact?: string;
}

interface InsightCategory {
  type: 'peak_hours' | 'buildings' | 'trends' | 'recommendations';
  title: string;
  items: InsightItem[];
}

interface InsightsData {
  summary: string;
  categories: InsightCategory[];
}

const Insights = () => {
  const navigate = useNavigate();
  const [insights, setInsights] = useState<InsightsData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [hasGenerated, setHasGenerated] = useState(false);

  const generateInsights = async () => {
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/get-insights');
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to generate insights');
      }

      const data = await response.json();
      setInsights(data.insights);
      setHasGenerated(true);
    } catch (err: any) {
      setError(err.message || 'Failed to generate insights. Please ensure the backend is running and try again.');
      console.error('Error generating insights:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const getCategoryIcon = (type: string) => {
    switch (type) {
      case 'peak_hours':
        return Clock;
      case 'buildings':
        return Building2;
      case 'trends':
        return TrendingUp;
      case 'recommendations':
        return Lightbulb;
      default:
        return Sparkles;
    }
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-6xl mx-auto mb-8">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          <span className="text-sm">Back to Dashboard</span>
        </button>

        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-primary-foreground" />
          </div>
          <h1 className="font-display text-3xl font-black tracking-wider cyber-text">
            AI INSIGHTS
          </h1>
        </div>
        <p className="text-muted-foreground text-sm">
          AI-powered analysis of your campus carbon emissions
        </p>
      </div>

      <div className="max-w-6xl mx-auto">
        {!hasGenerated && !isLoading && (
          <div className="glass-panel p-12 text-center">
            <Sparkles className="w-16 h-16 mx-auto mb-4 text-primary" />
            <h2 className="text-xl font-bold mb-2">Generate AI Insights</h2>
            <p className="text-muted-foreground mb-6">
              Get comprehensive analysis and recommendations for reducing your campus carbon footprint
            </p>
            <button
              onClick={generateInsights}
              className="px-6 py-3 bg-gradient-to-r from-primary to-secondary text-primary-foreground rounded-lg font-medium hover:opacity-90 transition-opacity"
            >
              Generate Insights
            </button>
          </div>
        )}

        {isLoading && (
          <div className="glass-panel p-12 text-center">
            <Loader2 className="w-12 h-12 mx-auto mb-4 text-primary animate-spin" />
            <h2 className="text-xl font-bold mb-2">Generating Insights...</h2>
            <p className="text-muted-foreground">
              Analyzing your emissions data with AI. This may take a moment.
            </p>
          </div>
        )}

        {error && (
          <div className="glass-panel p-6 border-l-4 border-destructive">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-destructive mt-0.5" />
              <div>
                <h3 className="font-bold text-destructive mb-1">Error</h3>
                <p className="text-sm text-muted-foreground">{error}</p>
                <button
                  onClick={generateInsights}
                  className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm hover:opacity-90 transition-opacity"
                >
                  Try Again
                </button>
              </div>
            </div>
          </div>
        )}

        {hasGenerated && insights && (
          <div className="space-y-6 animate-fade-in">
            {/* Summary Card */}
            <div className="glass-panel p-8 bg-gradient-to-br from-primary/10 to-secondary/10 border border-primary/20">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-6 h-6 text-primary-foreground" />
                </div>
                <div>
                  <h2 className="font-display text-xl font-bold mb-2">Summary</h2>
                  <p className="text-muted-foreground leading-relaxed">
                    {insights.summary}
                  </p>
                </div>
              </div>
            </div>

            {/* Insights Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {insights.categories.map((category, index) => (
                <InsightCard
                  key={index}
                  icon={getCategoryIcon(category.type)}
                  title={category.title}
                  items={category.items}
                  type={category.type}
                />
              ))}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 justify-center pt-4">
              <button
                onClick={generateInsights}
                className="px-6 py-3 glass-panel hover:bg-muted/50 transition-colors rounded-lg text-sm font-medium"
              >
                Regenerate Insights
              </button>
              <button
                onClick={() => navigate('/')}
                className="px-6 py-3 bg-gradient-to-r from-primary to-secondary text-primary-foreground rounded-lg text-sm font-medium hover:opacity-90 transition-opacity"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Insights;

