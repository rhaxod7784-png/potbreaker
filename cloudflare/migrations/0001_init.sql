CREATE TABLE IF NOT EXISTS visits (
  visitor_id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now'))
);
CREATE TABLE IF NOT EXISTS game_runs (
  run_id TEXT PRIMARY KEY,
  visitor_id TEXT,
  difficulty TEXT NOT NULL CHECK (difficulty IN ('normal','hard','very_hard')),
  status TEXT NOT NULL DEFAULT 'playing' CHECK (status IN ('playing','win','lose')),
  elapsed_ms INTEGER,
  started_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now')),
  finished_at TEXT
);
CREATE TABLE IF NOT EXISTS game_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  visitor_id TEXT,
  run_id TEXT,
  event_type TEXT NOT NULL,
  difficulty TEXT,
  elapsed_ms INTEGER,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now'))
);
CREATE INDEX IF NOT EXISTS game_events_created_at ON game_events(created_at);
CREATE TABLE IF NOT EXISTS rankings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL UNIQUE,
  nickname TEXT NOT NULL,
  difficulty TEXT NOT NULL CHECK (difficulty IN ('normal','hard','very_hard')),
  elapsed_ms INTEGER NOT NULL,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now')),
  FOREIGN KEY (run_id) REFERENCES game_runs(run_id)
);
CREATE INDEX IF NOT EXISTS rankings_order ON rankings(difficulty, elapsed_ms);
