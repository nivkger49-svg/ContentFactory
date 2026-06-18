# Cursor Rules Template

Use this as a starting point for `.cursor/rules/` in a new clone.

## Pipeline Rule

Every render starts with asset selection, not FFmpeg.

Required order:

1. Write a shot list: hook, scenes, durations, mood, roles, casting/context needs.
2. Run `scripts/pick_assets.py rank` for each scene.
3. Use local DB assets when `decision = pick_local`.
4. Use Pexels only when `decision = stale` or `gap`.
5. Run `intake_assets.py` after downloading new assets.
6. Audit every new video into `asset_scenes` before final render.
7. Create a storyboard JSON with `asset_id`, `role`, `pick_score`, `pick_decision`, `path`, `ss`, and `t`.
8. Render.
9. Run `pick_assets.py record` after keeping a draft.

## Market Profile

Each project should define its own market profile:

- language;
- target country/region;
- casting/context fit;
- brand safety rules;
- visual style;
- CTA wording.

Do not assume the original project's niche, language, or casting rules apply to a new project.

## Hard Stops

- Do not use `.env` values in committed code.
- Do not commit heavy media, local database files, or rendered outputs.
- Do not use assets tagged as rejected for the current market.
- Do not use a freshly downloaded external clip before scene audit.

## Useful Commands

```powershell
C:\Python314\python.exe F:\ContentFactory\scripts\pick_assets.py rank --role hook --themes "phone,scroll,curiosity" --batch ubt-001 --limit 10
C:\Python314\python.exe F:\ContentFactory\scripts\pick_assets.py record --storyboard F:\ContentFactory\batches\ubt-001\storyboard_example.json
```
