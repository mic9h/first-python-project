import { useState, useEffect } from 'react';
import { getInsights, runAnalysis } from '../lib/api';
import { Brain, RefreshCw, Zap } from 'lucide-react';
import type { Learning } from '../types';

const CATEGORY_COLORS: Record<string, string> = {
  content_type: 'bg-pink-500/10 text-pink-400',
  posting_time: 'bg-cyan-500/10 text-cyan-400',
  hashtag: 'bg-green-500/10 text-green-400',
  format: 'bg-yellow-500/10 text-yellow-400',
  hook: 'bg-orange-500/10 text-orange-400',
};

function ConfidenceBar({ value }: { value: number }) {
  return (
    <div className="flex items-center gap-2">
      <div className="w-20 h-1.5 bg-gray-700 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-pink-500 to-violet-500 rounded-full"
          style={{ width: `${value * 100}%` }}
        />
      </div>
      <span className="text-xs text-gray-500">{(value * 100).toFixed(0)}%</span>
    </div>
  );
}

export function LearningLog() {
  const [insights, setInsights] = useState<Learning[]>([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<string | null>(null);

  async function load() {
    try {
      const data = await getInsights();
      setInsights(data);
    } catch {
      setError('Could not load insights.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleAnalyze() {
    setAnalyzing(true);
    setResult(null);
    try {
      const data = await runAnalysis();
      setResult(`Analysis complete: ${data.new_insights} new insight(s) found.`);
      await load();
    } catch {
      setError('Analysis failed. Make sure you have at least 3 videos.');
    } finally {
      setAnalyzing(false);
    }
  }

  if (loading) return <div className="text-center text-gray-400 py-20">Loading insights...</div>;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Learning Insights</h2>
          <p className="text-sm text-gray-500">Patterns discovered from your video performance data</p>
        </div>
        <button
          onClick={handleAnalyze}
          disabled={analyzing}
          className="flex items-center gap-2 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          <RefreshCw size={16} className={analyzing ? 'animate-spin' : ''} />
          {analyzing ? 'Analyzing...' : 'Run Analysis'}
        </button>
      </div>

      {error && <div className="bg-red-500/10 text-red-400 p-3 rounded-lg text-sm">{error}</div>}
      {result && <div className="bg-green-500/10 text-green-400 p-3 rounded-lg text-sm">{result}</div>}

      {/* High Confidence Insights */}
      {insights.filter(i => i.confidence >= 0.6).length > 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <Zap size={18} className="text-yellow-400" />
            <h3 className="font-medium">What's Working</h3>
          </div>
          <div className="space-y-3">
            {insights.filter(i => i.confidence >= 0.6).map(insight => (
              <div key={insight.id} className="flex items-start gap-3 p-3 bg-gray-800/50 rounded-lg">
                <span className={`px-2 py-0.5 rounded text-xs whitespace-nowrap ${
                  CATEGORY_COLORS[insight.category] || 'bg-gray-700 text-gray-400'
                }`}>
                  {insight.category}
                </span>
                <div className="flex-1">
                  <p className="text-sm">{insight.insight}</p>
                  <ConfidenceBar value={insight.confidence} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* All Insights */}
      {insights.length === 0 ? (
        <div className="text-center py-16 text-gray-500">
          <Brain size={48} className="mx-auto mb-4 text-gray-600" />
          <p className="mb-2">No insights yet.</p>
          <p className="text-sm">Add at least 3 videos, then click "Run Analysis" to discover patterns.</p>
        </div>
      ) : (
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-gray-400">All Insights ({insights.length})</h3>
          {insights.map(insight => (
            <div key={insight.id} className="bg-gray-900 border border-gray-800 rounded-xl p-4">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-3 flex-1">
                  <span className={`px-2 py-0.5 rounded text-xs whitespace-nowrap mt-0.5 ${
                    CATEGORY_COLORS[insight.category] || 'bg-gray-700 text-gray-400'
                  }`}>
                    {insight.category}
                  </span>
                  <div>
                    <p className="text-sm">{insight.insight}</p>
                    <div className="flex items-center gap-4 mt-2">
                      <ConfidenceBar value={insight.confidence} />
                      <span className="text-xs text-gray-600">{insight.source}</span>
                      <span className="text-xs text-gray-600">
                        {new Date(insight.updated_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
