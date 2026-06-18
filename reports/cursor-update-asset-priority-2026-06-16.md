# Cursor Update: Asset Priority Workflow

Use this for future ContentFactory generations.

## New Rule

Before finalizing a storyboard, do not choose assets only by memory or by `asset_scenes.score`.

Use the asset ranker:

```powershell
C:\Python314\python.exe F:\ContentFactory\scripts\pick_assets.py rank --role hook --themes "instagram,phone,scroll" --batch ubt-007 --limit 10
```

For each scene, run rank with:

- `--role`: hook, bridge, contrast, product, punch, cta, transition, etc.
- `--themes`: comma-separated scene needs.
- `--batch`: current batch id, for example `ubt-007`.

## Decision Logic (v2 — 2026-06-16)

**Ranker does not replace Pexels.** Ranker checks local DB first; then freshness rules decide whether Pexels is required.

The ranker returns:

- `pick_local`: local candidates exist with acceptable score — still may require Pexels under batch rules below.
- `stale`: repetition risk is high — **Pexels mandatory** unless `manual_override_reason` in storyboard.
- `gap`: local DB fit is weak — **Pexels mandatory** unless `manual_override_reason` in storyboard.

### Batch freshness rules (every new video)

Unless Codex/human explicitly requests a **local remix only**:

1. **Minimum 1–2 new Pexels scenes** per batch (download → intake → audit before render).
2. **Hook scene**: always fresh Pexels search, unless explicit manual local lock with `manual_override_reason`.
3. **At least one bridge/emotion scene**: fresh Pexels search.
4. **Any scene** where ranker returns `stale` or `gap`: Pexels mandatory.
5. If top local assets were used in recent batches or look visually similar to recent drafts → Pexels search even when decision is `pick_local`.

### Hook hard rule

**Never use a hook asset with `repeat_penalty > 0`** without `manual_override_reason` in storyboard.

### Final pick

Compare **local ranked candidates + newly audited Pexels candidates** — choose best fit for VO meaning, not score alone.

## Important

Every final storyboard scene that uses a real asset should include:

```json
{
  "role": "hook",
  "asset_id": 364,
  "pick_score": 4.25,
  "pick_decision": "stale",
  "pexels_id": "7199063",
  "manual_override_reason": null,
  "path": "assets/raw/video/...",
  "ss": 0.8,
  "t": 3.71
}
```

If keeping a penalized or repeated local asset, set `manual_override_reason` (Ukrainian or English, one line why).

Generated cards may omit `asset_id`, but should still describe the background, planet/image, and duration.

## After Rendering

After a draft render is accepted or worth keeping, record usage:

```powershell
C:\Python314\python.exe F:\ContentFactory\scripts\pick_assets.py record --storyboard F:\ContentFactory\batches\<batch>\storyboard_*.json
```

This updates `batch_asset_usage`, which powers repeat penalties in future videos.

## Hard Filters

Never suggest or use assets tagged:

```text
reject_ua
```

For the Ukraine market, prefer visually relevant European/Ukrainian casting and context.

## Current Status

Implemented:

- `batch_asset_usage`
- `asset_pick_log` table
- `scripts/migrate_asset_priority.py`
- `scripts/pick_assets.py rank`
- `scripts/pick_assets.py record`
- `scripts/pick_assets.py backfill-usage`
- `scripts/pick_assets.py plan` basic JSON planner
- usage backfilled from UBT004, UBT005, UBT006 storyboards

Not implemented yet:

- full automatic storyboard generation
- semantic embeddings
- performance-weighted asset scoring
- karaoke / word-pop subtitle generation
