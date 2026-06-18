# Storyboard Schema

Last updated: 2026-06-16

Storyboards live under:

```text
F:\ContentFactory\batches\<batch_id>\storyboard_*.json
```

## Required Top-Level Fields

```json
{
  "batch": "ubt-006",
  "variant": "V01_cursor_full_cycle",
  "subtitle_mode": "bullets",
  "asset_selection": "assisted",
  "voice": "assets/voice/example.mp3",
  "subs": "batches/ubt-006/subs/example.ass",
  "scenes": []
}
```

## Scene Fields

Every real media scene should include:

```json
{
  "vo": "0.00-3.71",
  "role": "hook",
  "asset_id": 364,
  "pick_score": 4.5,
  "pick_decision": "pick_local",
  "path": "assets/raw/video/pexels/2026-06-16/example.mp4",
  "ss": 0.8,
  "t": 3.71
}
```

Generated cards may omit `asset_id`, but should still describe `type`, `bg`, `planet`, and `t`.

## Allowed Values

`subtitle_mode`:

- `bullets`
- `karaoke`
- `word_pop`
- `mixed`

`asset_selection`:

- `manual`
- `assisted`
- `auto`

For now, use `manual` or `assisted`. `auto` is reserved for a future full automatic storyboard builder.

## Rule

After a render is accepted as a draft, run:

```powershell
C:\Python314\python.exe F:\ContentFactory\scripts\pick_assets.py record --storyboard F:\ContentFactory\batches\<batch_id>\storyboard_*.json
```

This records usage so future videos can avoid repeating the same assets too often.
