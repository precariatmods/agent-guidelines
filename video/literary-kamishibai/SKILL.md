---
name: literary-kamishibai
description: Create a simple literary kamishibai video from a supplied story using scene images, VOICEVOX speech, subtitles, and the bundled Remotion workflow. Use for projects under this sample; do not add advanced production features unless requested.
---

# Literary Kamishibai

Read [POLICY.md](POLICY.md) and [Output.md](Output.md) first. Follow Policy as the source of truth for production decisions and Output as the source of truth for artifacts, destinations, completion criteria, and Git publication.

## Workflow

1. Identify the target project described by the artifact IDs in `Output.md`. Resolve and report its absolute output paths before writing. If it already contains work, do not overwrite it without the user's direction.
2. Run the environment check from the production root:

   ```powershell
   python scripts/check_environment.py
   ```

   Stop when a required environment is unavailable. Do not install external software automatically. Remotion is installed once in the shared `remotion/` directory; follow the command printed by the check only when it is missing.
3. Turn the supplied story into a script of approximately five minutes.
4. Write `dialogue.json` in playback order. Each entry must contain `line_id`, `scene_id`, `image`, `character`, and `text`. Keep `line_id` unique and use it as the WAV basename.
5. Write `voicevox_characters.csv` with exactly these columns: `シナリオ登場キャラ名`, `VoiceVOXキャラ名`, `VoiceVOXキャラID`.
6. Write one numbered instruction file per scene under `image_order/`. Include its `scene_id`, destination below `images/`, and the visual instruction.
7. Generate the requested scene images only when the user asks for image generation, and save each image at the path specified by its instruction file.
8. Confirm that VOICEVOX Engine is running, then generate speech from `text` without emotion, pitch, speed, or reading overrides:

   ```powershell
   python scripts/create_voice.py project/002
   ```

   Replace `002` with the target project ID.
9. Validate the JSON, CSV, images, and WAV files and prepare the shared Remotion runtime:

   ```powershell
   python scripts/prepare_remotion.py project/002
   ```

   Continue only when validation succeeds. This command generates `render_data.json` and places the current project under `remotion/public/current/`. Treat `render_data.json` as generated intermediate data; do not edit it directly.
10. When visual confirmation is useful, open the shared Remotion Studio:

    ```powershell
    cd remotion
    npm run studio
    ```

11. Render an MP4 only when the user requests it:

    ```powershell
    cd remotion
    npm run render -- ../project/002/output/video.mp4
    ```

    Replace `002` with the target project ID.

## Sources of truth

Input definitions, generated artifacts, destinations, and completion criteria are defined only in `Output.md`.

Do not report an image, audio file, Remotion placement, or MP4 as complete until the corresponding operation has actually succeeded.
