from __future__ import annotations

import argparse
import csv
import json
import math
import re
import shutil
import sys
import wave
from pathlib import Path, PurePosixPath
from typing import Any


FPS = 30
GAP_FRAMES = FPS
CSV_CHARACTER = "シナリオ登場キャラ名"
CSV_VOICEVOX_NAME = "VoiceVOXキャラ名"
CSV_VOICEVOX_ID = "VoiceVOXキャラID"
REQUIRED_LINE_KEYS = ("line_id", "scene_id", "image", "character", "text")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def safe_relative_image(value: str) -> PurePosixPath:
    normalized = value.replace("\\", "/")
    path = PurePosixPath(normalized)
    if path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] != "images":
        raise ValueError(f"imageはimages/内の相対パスにしてください: {value}")
    return path


def load_dialogue(path: Path) -> list[dict[str, str]]:
    data: Any = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, list) or not data:
        raise ValueError("dialogue.jsonは1件以上の配列にしてください。")
    lines: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, raw in enumerate(data, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"dialogue.jsonの{index}件目はオブジェクトではありません。")
        line: dict[str, str] = {}
        for key in REQUIRED_LINE_KEYS:
            value = raw.get(key)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"dialogue.jsonの{index}件目: {key}が空です。")
            line[key] = value.strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]+", line["line_id"]):
            raise ValueError(f"{line['line_id']}: line_idの形式が不正です。")
        if line["line_id"] in seen:
            raise ValueError(f"{line['line_id']}: line_idが重複しています。")
        seen.add(line["line_id"])
        safe_relative_image(line["image"])
        lines.append(line)
    return lines


def load_character_names(path: Path) -> set[str]:
    names: set[str] = set()
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        expected = {CSV_CHARACTER, CSV_VOICEVOX_NAME, CSV_VOICEVOX_ID}
        if set(reader.fieldnames or []) != expected:
            raise ValueError("voicevox_characters.csvの列は指定された3列だけにしてください。")
        for row_number, row in enumerate(reader, start=2):
            values = [(row.get(name) or "").strip() for name in expected]
            if not all(values):
                raise ValueError(f"voicevox_characters.csvの{row_number}行目に空欄があります。")
            name = (row.get(CSV_CHARACTER) or "").strip()
            if name in names:
                raise ValueError(f"{name}: 配役が重複しています。")
            try:
                speaker_id = int((row.get(CSV_VOICEVOX_ID) or "").strip())
            except ValueError as exc:
                raise ValueError(f"{row_number}行目のVoiceVOXキャラIDは整数ではありません。") from exc
            if speaker_id < 0:
                raise ValueError(f"{row_number}行目のVoiceVOXキャラIDは0以上にしてください。")
            names.add(name)
    return names


def wav_frames(path: Path) -> int:
    try:
        with wave.open(str(path), "rb") as wav:
            seconds = wav.getnframes() / wav.getframerate()
    except (wave.Error, ZeroDivisionError) as exc:
        raise ValueError(f"WAVを読み取れません: {path}") from exc
    return max(1, math.ceil(seconds * FPS))


def replace_current(source_project: Path, render_data: dict[str, Any], current: Path) -> None:
    temporary = current.with_name("current.new")
    if temporary.exists():
        shutil.rmtree(temporary)
    (temporary / "images").mkdir(parents=True)
    (temporary / "audio").mkdir(parents=True)

    used_images = {item["image"] for item in render_data["lines"]}
    for relative in used_images:
        source = source_project.joinpath(*PurePosixPath(relative).parts)
        destination = temporary.joinpath(*PurePosixPath(relative).parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    for item in render_data["lines"]:
        shutil.copy2(source_project / "audio" / item["audio"], temporary / "audio" / item["audio"])
    (temporary / "render_data.json").write_text(
        json.dumps(render_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    if current.exists():
        shutil.rmtree(current)
    temporary.rename(current)


def main() -> int:
    parser = argparse.ArgumentParser(description="素材を検査し、共通Remotionへ配置します。")
    parser.add_argument("project_dir", type=Path)
    args = parser.parse_args()

    try:
        project_dir = args.project_dir.resolve()
        root = Path(__file__).resolve().parent.parent
        current = root / "remotion" / "public" / "current"
        dialogue = load_dialogue(project_dir / "dialogue.json")
        characters = load_character_names(project_dir / "voicevox_characters.csv")

        errors: list[str] = []
        for line in dialogue:
            if line["character"] not in characters:
                errors.append(f"{line['line_id']}: 配役がありません: {line['character']}")
            image_path = project_dir.joinpath(*safe_relative_image(line["image"]).parts)
            if not image_path.is_file():
                errors.append(f"{line['line_id']}: 画像がありません: {line['image']}")
            audio_path = project_dir / "audio" / f"{line['line_id']}.wav"
            if not audio_path.is_file():
                errors.append(f"{line['line_id']}: 音声がありません: audio/{line['line_id']}.wav")
        if errors:
            raise ValueError("素材が不足しています。\n" + "\n".join(errors))

        render_lines: list[dict[str, Any]] = []
        cursor = 0
        for index, line in enumerate(dialogue):
            audio_name = f"{line['line_id']}.wav"
            audio_frame_count = wav_frames(project_dir / "audio" / audio_name)
            gap = 0 if index == len(dialogue) - 1 else GAP_FRAMES
            render_lines.append(
                {
                    **line,
                    "audio": audio_name,
                    "start_frame": cursor,
                    "audio_frames": audio_frame_count,
                    "duration_frames": audio_frame_count + gap,
                }
            )
            cursor += audio_frame_count + gap

        render_data = {"fps": FPS, "total_frames": cursor, "lines": render_lines}
        replace_current(project_dir, render_data, current)
        (project_dir / "render_data.json").write_text(
            json.dumps(render_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"CHECK OK: {len(render_lines)}セリフ、{cursor / FPS:.2f}秒")
        print(f"Remotion配置先: {current}")
        return 0
    except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
