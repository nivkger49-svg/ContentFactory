# Creative Package Spec

Every final ContentFactory video should ship with an adjacent metadata file:

- `video_name.mp4`
- `video_name.creative.json`

Purpose:
- give `neirokid-ads-agent` structured source-of-truth metadata
- avoid guessing hook, pain, angle, format, and CTA from STT alone

Priority order for Ads Agent:
1. `video_name.creative.json`
2. manual override
3. local intake / STT analysis
4. filename fallback

Minimum required fields:
- `creative_id`
- `source_video`
- `title`
- `language`
- `format`
- `pain`
- `angle`
- `hook`
- `offer`
- `cta`
- `voiceover_text`

Validation rules:
- `creative_id` must be non-empty
- `source_video` must exactly match the video filename
- `cta` should use enum values: `LEARN_MORE`, `SIGN_UP`, `DOWNLOAD`, `APPLY_NOW`
- `production_status` may be only `DRAFT` or `FINAL`

NeiroKid default CTA:
- `LEARN_MORE`

Mandatory packaging rule:
- every final video created by the flow must have an adjacent `.creative.json` file
- the final package is invalid if the MP4 exists without the sidecar
- this applies to all future renders, not only manually curated ones
- downstream agents should treat missing sidecar metadata as a packaging failure, not as a normal fallback case
