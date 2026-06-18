# Asset Intake Workflow

## Principle

New media should be imported incrementally. Do not re-review the whole library every time.

## Drop Folders

Use these folders for new material:

```text
F:\ContentFactory\assets\raw\video
F:\ContentFactory\assets\raw\images
F:\ContentFactory\assets\raw\site-recordings
F:\ContentFactory\assets\generated\images
F:\ContentFactory\assets\voice
F:\ContentFactory\references\fb-library
```

## Import Command

After adding new videos/images, run:

```powershell
C:\Python314\python.exe F:\ContentFactory\scripts\intake_assets.py F:\ContentFactory\assets
```

The script updates only by file path and records an intake run in SQLite.

## License Defaults

- `assets/raw/video` -> `pexels_license` for the current workflow, because the first video pack is from Pexels.
- `assets/raw/images` -> `needs_source_check` until source is known.
- `assets/generated/images` -> `ai_generated_review`.
- `assets/raw/site-recordings` -> `owned_site_recording`, but `needs_trim=true` in notes.

## Review Layers

1. Technical import: path, file type, duration/size when possible.
2. Visual tagging: mood, topic, text-safe zones, route fit.
3. Creative use: assign to hypotheses and actual videos.
4. Performance learning: update based on organic and paid results.

## External Stock Rule

For Pexels or any other external stock source, the factory must use this sequence:

1. Search existing SQLite database first.
2. If the needed scene is missing, search the external source.
3. Download only shortlisted assets.
4. Analyze every downloaded video before final render use.
5. Import scene-level notes into the database.
6. Use the asset only after it has searchable tags and scene notes.

This rule exists to prevent repeating the same visuals and to make every new download improve the library.
