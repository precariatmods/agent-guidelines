---
name: literary-kamishibai
description: Create and continue public-domain literary kamishibai projects from source verification and adaptation through image planning, VOICEVOX audio, sound effects, and Remotion video. Use when starting from the bundled basetemplate, organizing drafts in sozai, consulting on a story, or producing a named segment. Do not use for unrelated short-form drama writing.
---

# Literary Kamishibai

Turn a public-domain literary work into a reviewable illustrated-story project while preserving the source's language, relationships, and ending.

## Resolve local context

1. Find the workspace root.
2. If `scenario/README.md` exists, read it completely before acting. Treat it and the selected project's `story/local_rules.md` as higher priority than this portable skill.
3. For a new project, read [references/workflow.md](references/workflow.md). For audio, sound effects, or Remotion, also read [references/local-tools.md](references/local-tools.md).

The repository-level SECURITY.md is an optional first-use review note, not a runtime dependency. Users may remove their local copy after review. Do not require it or recreate it during ordinary production.

## Start a project

Use the bundled `assets/basetemplate/`; do not modify that source template for an individual work.

Run `scripts/create_project.py` with a workspace root, safe project ID, and title. It must create:

```text
<workspace>/scenario/projects/<project_id>/
```

The helper refuses to overwrite an existing destination, fills `job.json`, and can place a supplied original-text file or brief into `sozai/`. If the user has already supplied source notes, casting ideas, scene ideas, dialogue, image notes, or reference images, put what is known into matching paths under `sozai/`. Mark unknowns as unresolved; do not invent bibliographic facts.

After creation, rename references to `basetemplate` conceptually to the new project ID. Keep `sozai/` as the draft intake area until the user approves promotion into `source/`, `story/`, `input/`, `images/`, or `character_images/`.

## Consult and adapt

Work in small, reviewable decisions rather than generating the whole production at once:

```text
source and rights
→ passages worth preserving
→ characters and relationships
→ emotional arc
→ scenes
→ dialogue and narration
→ sound effects and pauses
→ estimated timing
→ image prompts
```

Preserve literary phrasing in narration when it carries rhythm, metaphor, irony, or aftertaste. Convert metaphors into concrete visual evidence before writing image prompts. Remove narration that merely repeats what the image communicates.

Before generating any image, present the consolidated scenario, character direction, and image plan for final user confirmation. After approval, explain the impact before accepting a major story, cast, or visual-direction change.

## Produce audio and video

Treat silence and sound effects as authored timing data, not padding inside voice files. Keep `text` for subtitles/display and `reading` for VOICEVOX pronunciation. Generate audio only for the requested segment unless the user explicitly requests the whole work.

Do not distribute, recommend, fetch, or execute private user-authored executables. Python source helpers may be used after inspection. Use only the required tools named in the public README and direct users to their official distribution sources. Keep VOICEVOX Engine requests on `localhost` unless the user knowingly approves a specific remote endpoint after being told what text will be sent.

Use the exact stopping boundary in the request:

- `segment_001 作成`: prepare only that segment and its missing assets.
- `segment_001 音声作成`: create only its voice files and timing data.
- `segment_001 Remotion配置`: prepare placement, snapshots, manifests, and optional check frames; do not render an MP4.
- `segment_001 動画化してください`: render that segment and preserve its intermediate Remotion state.

Use 16:9 horizontal art as the master. Derive vertical shorts by crop, pan, zoom, and fade unless a project rule says otherwise.

## Completion

Verify credits, manifests, final timing, segment status, image/source provenance, and reproducibility. Archive the work-specific Remotion state to the project's restore area before clearing the active Remotion entrypoint. Never delete a project or render state merely because production finished.
