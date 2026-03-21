import { useState, useEffect } from 'react';
import { getIdeas, generateIdeas, updateIdeaStatus } from '../lib/api';
import { Sparkles, ArrowRight } from 'lucide-react';
import type { ContentIdea } from '../types';

const STATUS_FLOW = ['idea', 'planned', 'filming', 'editing', 'posted'] as const;
const STATUS_COLORS: Record<string, string> = {
  idea: 'bg-blue-500/10 text-blue-400',
  planned: 'bg-yellow-500/10 text-yellow-400',
  filming: 'bg-orange-500/10 text-orange-400',
  editing: 'bg-purple-500/10 text-purple-400',
  posted: 'bg-green-500/10 text-green-400',
};

export function ContentIdeas() {
  const [ideas, setIdeas] = useState<ContentIdea[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string | undefined>(undefined);

  async function load() {
    try {
      const data = await getIdeas(filter);
      setIdeas(data);
    } catch {
      setError('Could not load ideas.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [filter]);

  async function handleGenerate() {
    setGenerating(true);
    try {
      await generateIdeas(5);
      await load();
    } catch {
      setError('Failed to generate ideas. Check your API key.');
    } finally {
      setGenerating(false);
    }
  }

  async function advanceStatus(idea: ContentIdea) {
    const idx = STATUS_FLOW.indexOf(idea.status as typeof STATUS_FLOW[number]);
    if (idx < STATUS_FLOW.length - 1) {
      const next = STATUS_FLOW[idx + 1];
      await updateIdeaStatus(idea.id, next);
      await load();
    }
  }

  if (loading) return <div className="text-center text-gray-400 py-20">Loading ideas...</div>;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Content Ideas</h2>
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="flex items-center gap-2 bg-pink-600 hover:bg-pink-500 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          <Sparkles size={16} />
          {generating ? 'Generating...' : 'Generate with AI'}
        </button>
      </div>

      {/* Filter */}
      <div className="flex gap-2">
        <button
          onClick={() => setFilter(undefined)}
          className={`px-3 py-1 rounded-full text-xs font-medium ${!filter ? 'bg-pink-500/20 text-pink-400' : 'bg-gray-800 text-gray-400'}`}
        >
          All
        </button>
        {STATUS_FLOW.map(s => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={`px-3 py-1 rounded-full text-xs font-medium ${filter === s ? 'bg-pink-500/20 text-pink-400' : 'bg-gray-800 text-gray-400'}`}
          >
            {s}
          </button>
        ))}
      </div>

      {error && <div className="bg-red-500/10 text-red-400 p-3 rounded-lg text-sm">{error}</div>}

      {/* Ideas List */}
      {ideas.length === 0 ? (
        <div className="text-center py-16 text-gray-500">
          <Sparkles size={48} className="mx-auto mb-4 text-gray-600" />
          <p>No content ideas yet. Click "Generate with AI" to get started!</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {ideas.map((idea) => (
            <div key={idea.id} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-medium">{idea.title}</h3>
                    <span className={`px-2 py-0.5 rounded text-xs ${STATUS_COLORS[idea.status] || 'bg-gray-800 text-gray-400'}`}>
                      {idea.status}
                    </span>
                    <span className="bg-gray-800 text-gray-400 px-2 py-0.5 rounded text-xs">
                      {idea.content_type}
                    </span>
                    {idea.generated_by === 'ai' && (
                      <span className="bg-violet-500/10 text-violet-400 px-2 py-0.5 rounded text-xs">AI</span>
                    )}
                  </div>
                  {idea.description && (
                    <p className="text-sm text-gray-400 mb-2">{idea.description}</p>
                  )}
                  {idea.hashtags.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {idea.hashtags.map((h, i) => (
                        <span key={i} className="text-xs text-pink-400">#{h}</span>
                      ))}
                    </div>
                  )}
                </div>
                {idea.status !== 'posted' && (
                  <button
                    onClick={() => advanceStatus(idea)}
                    className="flex items-center gap-1 text-sm text-gray-400 hover:text-white bg-gray-800 hover:bg-gray-700 px-3 py-1.5 rounded-lg transition-colors"
                  >
                    <ArrowRight size={14} />
                    Next
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
