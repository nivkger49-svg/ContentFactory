-- Content Factory SQLite schema

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS videos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'idea',
  platform TEXT,
  format TEXT NOT NULL DEFAULT 'vertical_9_16',
  topic TEXT,
  hook TEXT,
  script TEXT,
  cta TEXT,
  voice TEXT,
  duration_seconds INTEGER,
  project_dir TEXT,
  draft_path TEXT,
  final_path TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  path TEXT NOT NULL UNIQUE,
  asset_type TEXT,
  source TEXT,
  license_status TEXT NOT NULL DEFAULT 'unknown',
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS asset_scenes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  asset_id INTEGER NOT NULL,
  start_time REAL NOT NULL DEFAULT 0,
  end_time REAL,
  role TEXT,
  visual TEXT,
  emotion TEXT,
  themes TEXT,
  score REAL NOT NULL DEFAULT 3,
  comment TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_asset_scenes_asset
  ON asset_scenes(asset_id);

CREATE INDEX IF NOT EXISTS idx_asset_scenes_role
  ON asset_scenes(role);

CREATE TABLE IF NOT EXISTS video_assets (
  video_id INTEGER NOT NULL,
  asset_id INTEGER NOT NULL,
  role TEXT,
  notes TEXT,
  PRIMARY KEY (video_id, asset_id),
  FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE,
  FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS metrics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  video_id INTEGER NOT NULL,
  platform TEXT NOT NULL,
  published_at TEXT,
  views INTEGER,
  impressions INTEGER,
  ctr REAL,
  avg_watch_seconds REAL,
  retention_3s REAL,
  retention_25 REAL,
  retention_50 REAL,
  retention_75 REAL,
  retention_100 REAL,
  likes INTEGER,
  comments INTEGER,
  shares INTEGER,
  saves INTEGER,
  follows INTEGER,
  ad_spend REAL,
  leads INTEGER,
  conversions INTEGER,
  notes TEXT,
  recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS experiments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  hypothesis TEXT,
  variable TEXT,
  winner_video_id INTEGER,
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (winner_video_id) REFERENCES videos(id)
);

CREATE TABLE IF NOT EXISTS asset_intake_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  root_path TEXT NOT NULL,
  asset_kind TEXT NOT NULL,
  files_seen INTEGER NOT NULL DEFAULT 0,
  files_added INTEGER NOT NULL DEFAULT 0,
  files_updated INTEGER NOT NULL DEFAULT 0,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS asset_tags (
  asset_id INTEGER NOT NULL,
  tag_type TEXT NOT NULL,
  tag_value TEXT NOT NULL,
  confidence REAL,
  source TEXT NOT NULL DEFAULT 'manual',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (asset_id, tag_type, tag_value),
  FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS creative_hypotheses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  funnel_source TEXT,
  pain TEXT,
  angle TEXT,
  hook TEXT,
  cta TEXT,
  status TEXT NOT NULL DEFAULT 'backlog',
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS hooks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  text TEXT NOT NULL UNIQUE,
  language TEXT NOT NULL DEFAULT 'ru',
  pain TEXT,
  angle TEXT,
  funnel_source TEXT,
  status TEXT NOT NULL DEFAULT 'backlog',
  score REAL NOT NULL DEFAULT 0,
  tested_count INTEGER NOT NULL DEFAULT 0,
  winner_count INTEGER NOT NULL DEFAULT 0,
  retired_reason TEXT,
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scripts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  hook_id INTEGER,
  language TEXT NOT NULL DEFAULT 'ru',
  body TEXT NOT NULL,
  cta TEXT,
  duration_target_seconds INTEGER,
  status TEXT NOT NULL DEFAULT 'backlog',
  score REAL NOT NULL DEFAULT 0,
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (hook_id) REFERENCES hooks(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS creative_variants (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  hypothesis_id INTEGER,
  hook_id INTEGER,
  script_id INTEGER,
  funnel_source TEXT,
  format TEXT,
  visual_style TEXT,
  voice_style TEXT,
  status TEXT NOT NULL DEFAULT 'backlog',
  score REAL NOT NULL DEFAULT 0,
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (hypothesis_id) REFERENCES creative_hypotheses(id) ON DELETE SET NULL,
  FOREIGN KEY (hook_id) REFERENCES hooks(id) ON DELETE SET NULL,
  FOREIGN KEY (script_id) REFERENCES scripts(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS hook_evaluations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  hook_id INTEGER NOT NULL,
  creative_variant_id INTEGER,
  platform TEXT,
  funnel_source TEXT,
  impressions INTEGER,
  views INTEGER,
  hook_hold_rate REAL,
  avg_watch_seconds REAL,
  completion_rate REAL,
  clicks INTEGER,
  leads INTEGER,
  purchases INTEGER,
  spend REAL,
  verdict TEXT,
  notes TEXT,
  recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (hook_id) REFERENCES hooks(id) ON DELETE CASCADE,
  FOREIGN KEY (creative_variant_id) REFERENCES creative_variants(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS batch_asset_usage (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  batch_id TEXT NOT NULL,
  variant TEXT,
  asset_id INTEGER NOT NULL,
  scene_role TEXT,
  scene_index INTEGER,
  storyboard_path TEXT,
  draft_path TEXT,
  used_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE,
  UNIQUE(batch_id, variant, asset_id, scene_index, storyboard_path)
);

CREATE INDEX IF NOT EXISTS idx_batch_asset_usage_batch
  ON batch_asset_usage(batch_id);

CREATE INDEX IF NOT EXISTS idx_batch_asset_usage_asset
  ON batch_asset_usage(asset_id, used_at DESC);

CREATE TABLE IF NOT EXISTS asset_pick_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  batch_id TEXT NOT NULL,
  scene_role TEXT NOT NULL,
  asset_id INTEGER,
  priority_score REAL,
  fit_score REAL,
  repeat_penalty REAL,
  variety_bonus REAL,
  decision TEXT NOT NULL,
  reason TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE SET NULL
);
