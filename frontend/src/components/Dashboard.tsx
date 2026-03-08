import { useState, useEffect } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from 'recharts';
import { TrendingUp, TrendingDown, Eye, Heart, Users, Video } from 'lucide-react';
import { getOverview, getDailyStats, getContentPerformance, getVideos } from '../lib/api';
import type { OverviewStats, DailyStats, ContentTypePerformance, Video as VideoType } from '../types';

function StatCard({ label, value, icon, trend }: {
  label: string; value: string; icon: React.ReactNode; trend?: number;
}) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="flex items-center justify-between mb-2">
        <span className="text-gray-400 text-sm">{label}</span>
        <span className="text-gray-500">{icon}</span>
      </div>
      <div className="text-2xl font-bold">{value}</div>
      {trend !== undefined && (
        <div className={`flex items-center gap-1 mt-1 text-sm ${trend >= 0 ? 'text-green-400' : 'text-red-400'}`}>
          {trend >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
          {trend >= 0 ? '+' : ''}{trend}
        </div>
      )}
    </div>
  );
}

export function Dashboard() {
  const [overview, setOverview] = useState<OverviewStats | null>(null);
  const [dailyStats, setDailyStats] = useState<DailyStats[]>([]);
  const [contentPerf, setContentPerf] = useState<ContentTypePerformance[]>([]);
  const [videos, setVideos] = useState<VideoType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [o, d, c, v] = await Promise.all([
          getOverview(),
          getDailyStats(30),
          getContentPerformance(),
          getVideos({ sort_by: 'posted_at', order: 'desc' }),
        ]);
        setOverview(o);
        setDailyStats(d.reverse());
        setContentPerf(c);
        setVideos(v);
      } catch (err) {
        setError('Could not load data. Is the backend running?');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return <div className="text-center text-gray-400 py-20">Loading dashboard...</div>;
  }

  if (error) {
    return (
      <div className="text-center py-20">
        <p className="text-red-400 mb-2">{error}</p>
        <p className="text-gray-500 text-sm">Make sure the FastAPI backend is running on port 8000</p>
      </div>
    );
  }

  const o = overview!;

  return (
    <div className="space-y-6">
      {/* Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label="Followers"
          value={o.current_followers.toLocaleString()}
          icon={<Users size={18} />}
          trend={o.follower_growth}
        />
        <StatCard
          label="Total Views"
          value={o.total_views.toLocaleString()}
          icon={<Eye size={18} />}
        />
        <StatCard
          label="Avg Engagement"
          value={`${(o.avg_engagement_rate * 100).toFixed(1)}%`}
          icon={<Heart size={18} />}
        />
        <StatCard
          label="Total Videos"
          value={o.total_videos.toString()}
          icon={<Video size={18} />}
        />
      </div>

      {/* Quick Insights */}
      {(o.best_content_type || o.best_posting_hour >= 0) && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h3 className="text-sm font-medium text-gray-400 mb-3">Quick Insights</h3>
          <div className="flex flex-wrap gap-3">
            {o.best_content_type && (
              <span className="bg-pink-500/10 text-pink-400 text-sm px-3 py-1 rounded-full">
                Best type: {o.best_content_type}
              </span>
            )}
            {o.best_posting_hour >= 0 && (
              <span className="bg-violet-500/10 text-violet-400 text-sm px-3 py-1 rounded-full">
                Best hour: {o.best_posting_hour}:00
              </span>
            )}
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Followers Over Time */}
        {dailyStats.length > 0 && (
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
            <h3 className="text-sm font-medium text-gray-400 mb-4">Followers Over Time</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={dailyStats}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="date" tick={{ fill: '#888', fontSize: 12 }} />
                <YAxis tick={{ fill: '#888', fontSize: 12 }} />
                <Tooltip
                  contentStyle={{ background: '#1a1a2e', border: '1px solid #333', borderRadius: 8 }}
                  labelStyle={{ color: '#aaa' }}
                />
                <Line type="monotone" dataKey="followers" stroke="#ec4899" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Content Type Performance */}
        {contentPerf.length > 0 && (
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
            <h3 className="text-sm font-medium text-gray-400 mb-4">Engagement by Content Type</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={contentPerf}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="content_type" tick={{ fill: '#888', fontSize: 12 }} />
                <YAxis tick={{ fill: '#888', fontSize: 12 }} />
                <Tooltip
                  contentStyle={{ background: '#1a1a2e', border: '1px solid #333', borderRadius: 8 }}
                  formatter={(value) => `${(Number(value) * 100).toFixed(1)}%`}
                />
                <Bar dataKey="avg_engagement" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Views Over Time */}
      {dailyStats.length > 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h3 className="text-sm font-medium text-gray-400 mb-4">Daily Views</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={dailyStats}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="date" tick={{ fill: '#888', fontSize: 12 }} />
              <YAxis tick={{ fill: '#888', fontSize: 12 }} />
              <Tooltip
                contentStyle={{ background: '#1a1a2e', border: '1px solid #333', borderRadius: 8 }}
              />
              <Line type="monotone" dataKey="total_views" stroke="#06b6d4" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Recent Videos Table */}
      {videos.length > 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h3 className="text-sm font-medium text-gray-400 mb-4">Recent Videos</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-gray-500 border-b border-gray-800">
                  <th className="text-left py-2 px-3">Title</th>
                  <th className="text-left py-2 px-3">Type</th>
                  <th className="text-right py-2 px-3">Views</th>
                  <th className="text-right py-2 px-3">Likes</th>
                  <th className="text-right py-2 px-3">Engagement</th>
                  <th className="text-left py-2 px-3">Posted</th>
                </tr>
              </thead>
              <tbody>
                {videos.slice(0, 10).map((v) => (
                  <tr key={v.id} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                    <td className="py-2 px-3 max-w-[200px] truncate">{v.title}</td>
                    <td className="py-2 px-3">
                      <span className="bg-gray-800 text-gray-300 px-2 py-0.5 rounded text-xs">
                        {v.content_type}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-right">{v.views.toLocaleString()}</td>
                    <td className="py-2 px-3 text-right">{v.likes.toLocaleString()}</td>
                    <td className="py-2 px-3 text-right">
                      <span className={v.engagement_rate > 0.05 ? 'text-green-400' : 'text-gray-400'}>
                        {(v.engagement_rate * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td className="py-2 px-3 text-gray-400">
                      {new Date(v.posted_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty State */}
      {videos.length === 0 && dailyStats.length === 0 && (
        <div className="text-center py-16">
          <Video size={48} className="text-gray-600 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-300 mb-2">No data yet</h2>
          <p className="text-gray-500">Go to "Add Data" to enter your first video metrics or daily stats.</p>
        </div>
      )}
    </div>
  );
}
