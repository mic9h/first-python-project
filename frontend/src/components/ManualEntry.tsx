import { useState } from 'react';
import { createVideo, createDailyStats, importCSV } from '../lib/api';
import { CheckCircle, Upload, AlertCircle } from 'lucide-react';

const CONTENT_TYPES = ['tutorial', 'review', 'day-in-life', 'trend', 'comedy', 'general'];

export function ManualEntry() {
  const [tab, setTab] = useState<'video' | 'daily' | 'csv'>('video');
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Video form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [postedAt, setPostedAt] = useState(new Date().toISOString().slice(0, 16));
  const [durationSec, setDurationSec] = useState(30);
  const [contentType, setContentType] = useState('tutorial');
  const [hashtagsStr, setHashtagsStr] = useState('');
  const [soundName, setSoundName] = useState('');
  const [views, setViews] = useState(0);
  const [likes, setLikes] = useState(0);
  const [comments, setComments] = useState(0);
  const [shares, setShares] = useState(0);
  const [saves, setSaves] = useState(0);

  // Daily stats state
  const [statDate, setStatDate] = useState(new Date().toISOString().slice(0, 10));
  const [followers, setFollowers] = useState(0);
  const [following, setFollowing] = useState(0);
  const [totalLikes, setTotalLikes] = useState(0);
  const [totalViews, setTotalViews] = useState(0);
  const [profileViews, setProfileViews] = useState(0);

  async function handleVideoSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setMessage(null);
    try {
      const hashtags = hashtagsStr.split(',').map(h => h.trim()).filter(Boolean);
      await createVideo({
        title, description,
        posted_at: new Date(postedAt).toISOString(),
        duration_sec: durationSec,
        content_type: contentType,
        hashtags, sound_name: soundName,
        views, likes, comments, shares, saves,
      });
      setMessage({ type: 'success', text: 'Video added!' });
      setTitle(''); setDescription(''); setViews(0); setLikes(0);
      setComments(0); setShares(0); setSaves(0);
    } catch {
      setMessage({ type: 'error', text: 'Failed to add video. Check backend connection.' });
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDailySubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setMessage(null);
    try {
      await createDailyStats({
        date: statDate, followers, following,
        total_likes: totalLikes, total_views: totalViews,
        profile_views: profileViews,
      });
      setMessage({ type: 'success', text: 'Daily stats recorded!' });
    } catch {
      setMessage({ type: 'error', text: 'Failed to save stats.' });
    } finally {
      setSubmitting(false);
    }
  }

  async function handleCSVUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setSubmitting(true);
    setMessage(null);
    try {
      const result = await importCSV(file);
      setMessage({ type: 'success', text: result.message });
    } catch {
      setMessage({ type: 'error', text: 'CSV import failed.' });
    } finally {
      setSubmitting(false);
    }
  }

  const inputClass = 'w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-pink-500';
  const labelClass = 'block text-sm text-gray-400 mb-1';

  return (
    <div className="max-w-2xl mx-auto">
      {/* Tab Selector */}
      <div className="flex gap-2 mb-6">
        {(['video', 'daily', 'csv'] as const).map((t) => (
          <button
            key={t}
            onClick={() => { setTab(t); setMessage(null); }}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              tab === t ? 'bg-pink-500/20 text-pink-400' : 'bg-gray-800 text-gray-400 hover:text-white'
            }`}
          >
            {t === 'video' ? 'Add Video' : t === 'daily' ? 'Daily Stats' : 'Import CSV'}
          </button>
        ))}
      </div>

      {/* Message */}
      {message && (
        <div className={`flex items-center gap-2 p-3 rounded-lg mb-4 ${
          message.type === 'success' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
        }`}>
          {message.type === 'success' ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
          {message.text}
        </div>
      )}

      {/* Video Form */}
      {tab === 'video' && (
        <form onSubmit={handleVideoSubmit} className="space-y-4 bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-2">Add Video Metrics</h2>

          <div>
            <label className={labelClass}>Title *</label>
            <input className={inputClass} value={title} onChange={e => setTitle(e.target.value)} required />
          </div>

          <div>
            <label className={labelClass}>Description</label>
            <textarea className={inputClass} rows={2} value={description} onChange={e => setDescription(e.target.value)} />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>Posted At</label>
              <input type="datetime-local" className={inputClass} value={postedAt} onChange={e => setPostedAt(e.target.value)} />
            </div>
            <div>
              <label className={labelClass}>Duration (sec)</label>
              <input type="number" className={inputClass} value={durationSec} onChange={e => setDurationSec(+e.target.value)} min={0} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>Content Type</label>
              <select className={inputClass} value={contentType} onChange={e => setContentType(e.target.value)}>
                {CONTENT_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className={labelClass}>Sound Name</label>
              <input className={inputClass} value={soundName} onChange={e => setSoundName(e.target.value)} placeholder="Original sound" />
            </div>
          </div>

          <div>
            <label className={labelClass}>Hashtags (comma-separated)</label>
            <input className={inputClass} value={hashtagsStr} onChange={e => setHashtagsStr(e.target.value)} placeholder="tech, coding, python" />
          </div>

          <div className="grid grid-cols-5 gap-3">
            {[
              ['Views', views, setViews],
              ['Likes', likes, setLikes],
              ['Comments', comments, setComments],
              ['Shares', shares, setShares],
              ['Saves', saves, setSaves],
            ].map(([label, val, setter]) => (
              <div key={label as string}>
                <label className={labelClass}>{label as string}</label>
                <input type="number" className={inputClass} value={val as number}
                  onChange={e => (setter as (v: number) => void)(+e.target.value)} min={0} />
              </div>
            ))}
          </div>

          {views > 0 && (
            <div className="text-sm text-gray-400">
              Engagement Rate: <span className="text-pink-400 font-medium">
                {(((likes + comments + shares + saves) / views) * 100).toFixed(1)}%
              </span>
            </div>
          )}

          <button type="submit" disabled={submitting || !title}
            className="w-full bg-pink-600 hover:bg-pink-500 disabled:opacity-50 text-white font-medium py-2 rounded-lg transition-colors">
            {submitting ? 'Saving...' : 'Add Video'}
          </button>
        </form>
      )}

      {/* Daily Stats Form */}
      {tab === 'daily' && (
        <form onSubmit={handleDailySubmit} className="space-y-4 bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-2">Record Daily Stats</h2>
          <p className="text-sm text-gray-500 mb-4">
            Enter today's numbers from your TikTok profile.
          </p>

          <div>
            <label className={labelClass}>Date</label>
            <input type="date" className={inputClass} value={statDate} onChange={e => setStatDate(e.target.value)} />
          </div>

          <div className="grid grid-cols-2 gap-4">
            {[
              ['Followers', followers, setFollowers],
              ['Following', following, setFollowing],
              ['Total Likes', totalLikes, setTotalLikes],
              ['Total Views', totalViews, setTotalViews],
              ['Profile Views', profileViews, setProfileViews],
            ].map(([label, val, setter]) => (
              <div key={label as string}>
                <label className={labelClass}>{label as string}</label>
                <input type="number" className={inputClass} value={val as number}
                  onChange={e => (setter as (v: number) => void)(+e.target.value)} min={0} />
              </div>
            ))}
          </div>

          <button type="submit" disabled={submitting}
            className="w-full bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-medium py-2 rounded-lg transition-colors">
            {submitting ? 'Saving...' : 'Save Daily Stats'}
          </button>
        </form>
      )}

      {/* CSV Import */}
      {tab === 'csv' && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-2">Import from CSV</h2>
          <p className="text-sm text-gray-500 mb-4">
            Upload a CSV with columns: title, description, posted_at, duration_sec,
            content_type, hashtags, sound_name, views, likes, comments, shares, saves
          </p>
          <label className="flex flex-col items-center justify-center border-2 border-dashed border-gray-700 rounded-xl p-8 cursor-pointer hover:border-pink-500 transition-colors">
            <Upload size={32} className="text-gray-500 mb-2" />
            <span className="text-gray-400 text-sm">Click to upload CSV file</span>
            <input type="file" accept=".csv" className="hidden" onChange={handleCSVUpload} disabled={submitting} />
          </label>
        </div>
      )}
    </div>
  );
}
