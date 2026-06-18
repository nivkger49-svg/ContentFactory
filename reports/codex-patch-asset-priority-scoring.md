# Codex Patch: Asset Priority Scoring & Selection Queue

**Status:** draft for discussion  
**Author:** Cursor (generation lane)  
**Implementer:** Codex (technical lane)  
**Date:** 2026-06-16  
**Related:** `reports/factory-operating-protocol.md`, `reports/ubt-001-lessons-and-next-rules.md`, `.cursor/rules/content-factory-pipeline.mdc`

---

## 1. Problem

Today the pipeline implicitly treats **local DB as first choice** and Pexels as fallback. That is correct in principle, but selection often reduces to:

> pick highest `asset_scenes.score` that loosely matches the scene role

This causes:

- **visual repetition** across batches (same phone clip, same zodiac wheel, same walking shot);
- no structured **variety penalty** before render;
- no single ranked queue where **audited DB assets and fresh Pexels candidates** are compared by the same rules;
- storyboards do not record **why** an asset was chosen or rejected.

**This patch does NOT propose “API over DB”.**  
It proposes a **unified selection score** with DB-first sourcing and Pexels only when the queue says `gap` or `stale`.

---

## 2. Design principles

| Principle | Rule |
|-----------|------|
| DB first | Search SQLite before any Pexels search |
| One queue | DB hits and post-audit Pexels hits compete on the same formula |
| Audit gate | No render without `asset_scenes` row (unchanged) |
| Variety matters | Recent use lowers rank; does not hard-block unless configured |
| Casting hard stop | `casting_fit: reject_ua` → score = 0, never suggest |
| Pexels = expansion | API only for missing role or when best local pick is `stale` |
| Human override | Storyboard `asset_id` manual lock always wins |

---

## 3. Selection score (v1)

For a candidate asset `a` and scene requirement `s`:

```
priority_score = fit_score + variety_bonus - repeat_penalty
```

Clamp to `0..10`. Sort descending.

### 3.1 `fit_score` (0–5)

Start from `asset_scenes.score` (1–5). If multiple scene rows exist for one asset, use the row whose `role` best overlaps scene requirement.

Optional small boosts (Codex discretion, keep simple in v1):

| Signal | Boost |
|--------|-------|
| `role` contains required role (`hook`, `bridge`, `product moment`, …) | +0.5 |
| `themes` keyword overlap with scene brief | +0.25 per hit, max +1.0 |
| `asset_type = site_master_recording` and scene needs product UI | +0.5 |
| `asset_type = generated_image` and scene needs CTA bg | +0.5 |

Hard filters (exclude before scoring):

- `asset_tags.tag_value = 'reject_ua'`
- `asset_scenes.score <= 1`
- asset path missing on disk

### 3.2 `repeat_penalty` (0–3)

Read recent usage from new table `batch_asset_usage` (see §4).

| Last used in | Penalty |
|--------------|---------|
| current batch (same `batch_id`) | +3.0 (effectively block duplicate in one video) |
| previous batch (N-1) | +2.0 |
| 2 batches ago (N-2) | +1.0 |
| 3+ batches ago | +0.0 |

Config constant: `VARIETY_LOOKBACK_BATCHES = 3` (env or `config/factory.json`).

### 3.3 `variety_bonus` (0–1)

Reward assets **not seen in last N batches** when another candidate with same `fit_score` exists:

- if `last_used_batch` is NULL or older than lookback → +1.0
- else → +0.0

### 3.4 Gap / stale decision

After ranking local candidates for scene `s`:

| Condition | Action |
|-----------|--------|
| no candidates with `priority_score >= 3.0` | `gap` → allow Pexels search |
| best candidate `priority_score < 4.0` AND next-best is `>= 2.0` gap below | `stale` → suggest Pexels, still allow override |
| best `priority_score >= 4.0` | `pick_local` |
| all locals penalized by repeat | `stale` → Pexels or pick least-bad with warning |

Return machine-readable status: `pick_local` | `stale` | `gap`.

---

## 4. Schema changes

Add to `db/schema.sql` and migrate `factory.sqlite`.

### 4.1 `batch_asset_usage`

Tracks which assets appeared in which batch storyboard/render.

```sql
CREATE TABLE IF NOT EXISTS batch_asset_usage (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  batch_id TEXT NOT NULL,           -- e.g. 'ubt-006'
  variant TEXT,                     -- e.g. 'V01_cursor_full_cycle'
  asset_id INTEGER NOT NULL,
  scene_role TEXT,                  -- hook | bridge | product | cta | ...
  scene_index INTEGER,              -- 0-based position in storyboard
  storyboard_path TEXT,
  draft_path TEXT,
  used_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_batch_asset_usage_batch
  ON batch_asset_usage(batch_id);
CREATE INDEX IF NOT EXISTS idx_batch_asset_usage_asset
  ON batch_asset_usage(asset_id, used_at DESC);
```

### 4.2 `asset_pick_log` (optional but recommended)

Audit trail for generation agent / human review.

```sql
CREATE TABLE IF NOT EXISTS asset_pick_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  batch_id TEXT NOT NULL,
  scene_role TEXT NOT NULL,
  asset_id INTEGER,
  priority_score REAL,
  fit_score REAL,
  repeat_penalty REAL,
  variety_bonus REAL,
  decision TEXT NOT NULL,           -- pick_local | stale | gap | manual | rejected
  reason TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE SET NULL
);
```

### 4.3 Storyboard JSON extension

Documented contract for `batches/*/storyboard_*.json`:

```json
{
  "batch": "ubt-006",
  "variant": "V01_cursor_full_cycle",
  "subtitle_mode": "bullets",
  "asset_selection": "manual",
  "scenes": [
    {
      "vo": "0.00-3.71",
      "role": "hook",
      "asset_id": 364,
      "pick_score": 4.5,
      "pick_decision": "pick_local",
      "path": "...",
      "ss": 0.8,
      "t": 3.71
    }
  ]
}
```

| Field | Values | Notes |
|-------|--------|-------|
| `subtitle_mode` | `bullets` (default), `karaoke`, `word_pop`, `mixed` | Generation lane sets this; render validates ASS exists |
| `asset_selection` | `manual`, `assisted`, `auto` | v1: implement `assisted` + `manual`; `auto` phase 2 |

---

## 5. CLI: `scripts/pick_assets.py`

Codex implements a read-only ranker first, then optional write-back.

### 5.1 Commands

```bash
# Rank local assets for one scene brief
python scripts/pick_assets.py rank \
  --role hook \
  --themes "instagram,phone,scroll" \
  --batch ubt-007 \
  --limit 10

# Rank all scenes from a shot-list YAML/JSON brief
python scripts/pick_assets.py plan \
  --brief batches/ubt-007/shot_list.json \
  --batch ubt-007 \
  --out batches/ubt-007/asset_candidates.json

# After storyboard finalized — record usage
python scripts/pick_assets.py record \
  --storyboard batches/ubt-006/storyboard_ubt006_v01_cursor.json

# Backfill from existing storyboards (one-time)
python scripts/pick_assets.py backfill-usage \
  --batches-dir batches/
```

### 5.2 `rank` output (stdout JSON)

```json
{
  "batch": "ubt-007",
  "scene_role": "hook",
  "decision": "stale",
  "candidates": [
    {
      "asset_id": 364,
      "path": "assets/raw/video/pexels/...",
      "fit_score": 5.0,
      "repeat_penalty": 2.0,
      "variety_bonus": 0.0,
      "priority_score": 3.0,
      "last_used_batch": "ubt-006",
      "visual": "Hand scrolls Instagram grid..."
    }
  ],
  "pexels_recommended": true,
  "pexels_query_hint": "european woman annoyed phone scroll portrait"
}
```

### 5.3 Query inputs

Reuse existing tables:

- `assets`, `asset_scenes`, `asset_tags`, `batch_asset_usage`
- optional full-text: `visual`, `themes`, `emotion`, `role` (LIKE is fine for v1)

---

## 6. Workflow integration

### Generation lane (Cursor)

1. Write shot list with `role`, `themes`, `vo` window per scene.
2. Run `pick_assets.py plan` → get ranked candidates + `gap`/`stale` flags.
3. For `gap`/`stale` scenes → Pexels search/download → intake → audit → re-run `rank`.
4. Lock choices in storyboard (`asset_selection: assisted`, optional `pick_score`).
5. Set `subtitle_mode: bullets` unless A/B variant explicitly tests another mode.

### Technical lane (Codex)

1. Implement schema + migration script `scripts/migrate_asset_priority.py`.
2. Implement `pick_assets.py` + unit tests with fixture SQLite.
3. Implement `record` + `backfill-usage`.
4. Update `factory-operating-protocol.md` §Asset Priority (short section, link here).
5. Optional: pre-render validator in render scripts — warn if `asset_id` used in last batch without `manual` lock.

### Pexels rule (unchanged, clarified)

```
IF rank.decision IN (gap, stale) AND pexels_recommended:
    search Pexels (2-3 IDs per scene)
    download → intake_assets.py → audit → rank again
ELSE:
    use top local candidate
```

---

## 7. Subtitle mode (minimal v1)

**Default: `bullets`** — do not build karaoke/word-pop engines in this patch.

Codex only needs to:

1. Validate storyboard field `subtitle_mode`.
2. Document allowed values in storyboard JSON schema comment or `reports/storyboard-schema.md`.
3. (Optional) fail render if `subtitle_mode` set but subs file name does not match pattern, e.g. `*_bullets.ass`.

Karaoke (`{\k}` ASS) and word-pop (per-word events) remain **phase 2** experiments.

---

## 8. Backfill plan

One-time:

```bash
python scripts/pick_assets.py backfill-usage --batches-dir batches/
```

Parse existing storyboards:

- `ubt-001` … `ubt-006` → insert `batch_asset_usage` rows per scene with `asset_id`.

This unlocks variety penalty immediately for UBT007+.

---

## 9. Acceptance criteria

- [ ] `batch_asset_usage` populated for ubt-001…006 via backfill
- [ ] `pick_assets.py rank` returns sorted list with score breakdown
- [ ] asset 364 after ubt-006 shows `repeat_penalty >= 2` when ranking ubt-007 hook
- [ ] `reject_ua` assets never appear in candidates
- [ ] `record` idempotent per storyboard path + variant
- [ ] Protocol doc updated with link to this patch
- [ ] No change to render output when storyboard is `asset_selection: manual` (backward compatible)

---

## 10. Out of scope (phase 2)

- Automatic storyboard assembly (`asset_selection: auto`)
- Semantic / embedding search over `visual` text
- Karaoke and word-pop ASS generators
- Performance-weighted scoring (boost assets with good hook_hold from `metrics`)
- UI dashboard

---

## 11. Open questions for discussion

1. **Hard block vs soft penalty** — should same `asset_id` in N-1 batch be forbidden for hook role, or only penalized?
2. **Lookback window** — 3 batches enough, or time-based (e.g. 14 days)?
3. **Site recordings** — separate repeat pool (quiz.MP4) or same table?
4. **Generated images** — track usage in `batch_asset_usage` too? (recommended: yes)

---

## 12. Suggested Codex task order

1. Migration + backfill
2. `pick_assets.py rank` + tests
3. `plan` + `record`
4. Protocol doc + storyboard schema note
5. (Optional) render-time warning hook

---

## Appendix A — Example: UBT007 hook after UBT006

Scene: `hook`, themes `instagram, scroll, lie`

| asset_id | fit | repeat_penalty | priority | note |
|----------|-----|----------------|----------|------|
| 364 | 5.0 | 2.0 | 3.0 | used ubt-006 hook → stale |
| 20 | 5.0 | 0.0 | 6.0 | used ubt-005 bridge, not hook → OK |
| 365 | 5.0 | 2.0 | 3.0 | used ubt-006 bridge |

→ `decision: stale` for 364/365; suggest new Pexels OR promote 20 if role overlap acceptable.

---

## Appendix B — Config stub

`config/factory.json` (new file, optional):

```json
{
  "asset_priority": {
    "variety_lookback_batches": 3,
    "min_pick_score": 3.0,
    "stale_threshold": 4.0,
    "block_same_batch_duplicate": true
  },
  "subtitles": {
    "default_mode": "bullets"
  }
}
```
