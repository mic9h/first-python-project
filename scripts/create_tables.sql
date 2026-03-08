-- TikTok Growth Tracker - Database Schema
-- Run this in Supabase SQL Editor

-- Config table
CREATE TABLE IF NOT EXISTS config (
    id SERIAL PRIMARY KEY,
    tiktok_handle TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    settings JSONB DEFAULT '{}'
);

-- Videos table
CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    tiktok_id TEXT UNIQUE,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    posted_at TIMESTAMPTZ NOT NULL,
    duration_sec INTEGER DEFAULT 0,
    content_type TEXT DEFAULT 'general',
    hashtags TEXT[] DEFAULT '{}',
    sound_name TEXT DEFAULT '',
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    engagement_rate FLOAT DEFAULT 0.0,
    source TEXT DEFAULT 'manual',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_videos_posted_at ON videos(posted_at DESC);
CREATE INDEX IF NOT EXISTS idx_videos_content_type ON videos(content_type);

-- Daily stats table
CREATE TABLE IF NOT EXISTS daily_stats (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    followers INTEGER DEFAULT 0,
    following INTEGER DEFAULT 0,
    total_likes INTEGER DEFAULT 0,
    total_views INTEGER DEFAULT 0,
    profile_views INTEGER DEFAULT 0,
    new_followers INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_daily_stats_date ON daily_stats(date DESC);

-- Content ideas table
CREATE TABLE IF NOT EXISTS content_ideas (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    content_type TEXT DEFAULT 'general',
    estimated_effort TEXT DEFAULT 'medium',
    trending_score FLOAT DEFAULT 0.0,
    hashtags TEXT[] DEFAULT '{}',
    status TEXT DEFAULT 'idea',
    scheduled_for TIMESTAMPTZ,
    generated_by TEXT DEFAULT 'manual',
    created_at TIMESTAMPTZ DEFAULT now(),
    metadata JSONB DEFAULT '{}'
);

-- Learnings table
CREATE TABLE IF NOT EXISTS learnings (
    id SERIAL PRIMARY KEY,
    category TEXT NOT NULL,
    insight TEXT NOT NULL,
    evidence JSONB DEFAULT '{}',
    confidence FLOAT DEFAULT 0.5,
    source TEXT DEFAULT 'auto_analysis',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_learnings_active ON learnings(is_active, confidence DESC);

-- Session notes table
CREATE TABLE IF NOT EXISTS session_notes (
    id SERIAL PRIMARY KEY,
    session_date DATE DEFAULT CURRENT_DATE,
    notes TEXT DEFAULT '',
    action_items JSONB DEFAULT '[]',
    metrics_snapshot JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Algorithm knowledge table
CREATE TABLE IF NOT EXISTS algorithm_knowledge (
    id SERIAL PRIMARY KEY,
    topic TEXT NOT NULL,
    rule TEXT NOT NULL,
    details TEXT DEFAULT '',
    source TEXT DEFAULT 'community',
    confidence FLOAT DEFAULT 0.5,
    last_verified TIMESTAMPTZ,
    is_current BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Trends table
CREATE TABLE IF NOT EXISTS trends (
    id SERIAL PRIMARY KEY,
    trend_type TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    relevance_score FLOAT DEFAULT 0.0,
    discovered_at TIMESTAMPTZ DEFAULT now(),
    expires_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'
);
