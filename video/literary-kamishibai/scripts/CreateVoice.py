from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
import wave
from pathlib import Path
from typing import Any

from Voice import DEFAULT_ENGINE_URL, VoicevoxError, request_json, synthesize


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


BASE_PARAMS = {
    "speedScale": 1.0,
    "pitchScale": 0.0,
    "intonationScale": 1.0,
    "volumeScale": 1.0,
    "pauseLengthScale": 1.0,
}

POLICY_RATE = {
    "none": 0.0,
    "light": 0.5,
    "full": 1.0,
}

EMOTION_PARAM_KEYS = {
    "speed_delta": "speedScale",
    "pitch_delta": "pitchScale",
    "intonation_delta": "intonationScale",
    "volume_delta": "volumeScale",
    "pause_length_delta": "pauseLengthScale",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def load_csv_map(path: Path, key: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row_number, row in enumerate(load_csv_rows(path), start=2):
        value = str(row.get(key, "")).strip()
        if not value:
            raise ValueError(f"{path}: {row_number}行目の {key} が空です。")
        if value in result:
            raise ValueError(f"{path}: {key} '{value}' が重複しています。")
        result[value] = row
    return result


def load_voice_style_master(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    result: dict[tuple[str, str], dict[str, str]] = {}
    for row_number, row in enumerate(load_csv_rows(path), start=2):
        voicevox_character = str(row.get("voicevox_character", "")).strip()
        emotion = str(row.get("emotion", "")).strip()
        speaker_id = str(row.get("speaker_id", "")).strip()
        style_name = str(row.get("style_name", "")).strip()
        param_policy = str(row.get("param_policy", "")).strip()

        if not voicevox_character:
            raise ValueError(f"{path}: {row_number}行目の voicevox_character が空です。")
        if not emotion:
            raise ValueError(f"{path}: {row_number}行目の emotion が空です。")
        if not speaker_id:
            raise ValueError(f"{path}: {row_number}行目の speaker_id が空です。")
        try:
            parsed_speaker_id = int(speaker_id)
        except ValueError as exc:
            raise ValueError(
                f"{path}: {row_number}行目の speaker_id '{speaker_id}' は整数ではありません。"
            ) from exc
        if parsed_speaker_id < 0:
            raise ValueError(f"{path}: {row_number}行目の speaker_id は0以上で指定してください。")
        if not style_name:
            raise ValueError(f"{path}: {row_number}行目の style_name が空です。")
        if param_policy not in POLICY_RATE:
            raise ValueError(
                f"{path}: {row_number}行目の param_policy '{param_policy}' は "
                f"{', '.join(POLICY_RATE)} のいずれかで指定してください。"
            )

        master_key = (voicevox_character, emotion)
        if master_key in result:
            raise ValueError(
                f"{path}: voicevox_character + emotion "
                f"'{voicevox_character} + {emotion}' が重複しています。"
            )
        result[master_key] = row
    return result


def as_float(value: str | None, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    return float(value)


def calculate_params(emotion_row: dict[str, str], policy: str) -> dict[str, float]:
    rate = POLICY_RATE.get(policy, 1.0)
    params = dict(BASE_PARAMS)
    for delta_key, param_key in EMOTION_PARAM_KEYS.items():
        params[param_key] += as_float(emotion_row.get(delta_key, "0")) * rate
    return params


def validate_master_contents(
    character_master: dict[str, dict[str, str]],
    emotion_master: dict[str, dict[str, str]],
) -> None:
    errors: list[str] = []

    for character, row in character_master.items():
        voicevox_character = str(row.get("voicevox_character", "")).strip()
        default_speaker_id = str(row.get("default_speaker_id", "")).strip()
        credit = str(row.get("credit", "")).strip()
        if not voicevox_character:
            errors.append(f"character_master.csv: '{character}' の voicevox_character が空です。")
        if not default_speaker_id:
            errors.append(f"character_master.csv: '{character}' の default_speaker_id が空です。")
        else:
            try:
                parsed_default_id = int(default_speaker_id)
                if parsed_default_id < 0:
                    raise ValueError
            except ValueError:
                errors.append(
                    f"character_master.csv: '{character}' の default_speaker_id "
                    f"'{default_speaker_id}' は0以上の整数ではありません。"
                )
        if not credit:
            errors.append(f"character_master.csv: '{character}' の credit が空です。")

    for emotion, row in emotion_master.items():
        for delta_key in EMOTION_PARAM_KEYS:
            raw_value = str(row.get(delta_key, "")).strip()
            if not raw_value:
                errors.append(f"emotion_master.csv: '{emotion}' の {delta_key} が空です。")
                continue
            try:
                float(raw_value)
            except ValueError:
                errors.append(
                    f"emotion_master.csv: '{emotion}' の {delta_key} "
                    f"'{raw_value}' は数値ではありません。"
                )

    if errors:
        raise ValueError("\n".join(errors))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def load_segment_assets(project_dir: Path) -> list[dict[str, Any]]:
    segment_assets_path = project_dir / "input" / "remotion_segment_assets.json"
    if not segment_assets_path.exists():
        return []
    return load_json(segment_assets_path)


def build_line_order(
    project_dir: Path,
    dialogue: list[dict[str, Any]],
    segment_id: str | None = None,
    line_ids: list[str] | None = None,
) -> list[str]:
    if line_ids:
        return line_ids

    segment_assets = load_segment_assets(project_dir)
    if segment_id:
        for segment in segment_assets:
            if segment.get("segment_id") == segment_id:
                return list(segment.get("dialogue_line_ids", []))
        raise ValueError(f"{segment_id}: remotion_segment_assets.json に segment_id がありません。")

    if not segment_assets:
        return [line["line_id"] for line in dialogue]

    seen: set[str] = set()
    ordered: list[str] = []
    for segment in segment_assets:
        for line_id in segment.get("dialogue_line_ids", []):
            if line_id not in seen:
                seen.add(line_id)
                ordered.append(line_id)

    for line in dialogue:
        line_id = line["line_id"]
        if line_id not in seen:
            ordered.append(line_id)

    return ordered


def resolve_voice(
    line: dict[str, Any],
    character_master: dict[str, dict[str, str]],
    voice_style_master: dict[tuple[str, str], dict[str, str]],
    emotion_master: dict[str, dict[str, str]],
) -> dict[str, Any]:
    speaker = line["speaker"]
    emotion = line["emotion"]
    character_row = character_master[speaker]
    voicevox_character = character_row["voicevox_character"]
    style_row = voice_style_master[(voicevox_character, emotion)]

    speaker_id = style_row["speaker_id"]
    policy = style_row["param_policy"]
    params = calculate_params(emotion_master[emotion], policy)

    return {
        "speaker_id": int(speaker_id),
        "voicevox_character": voicevox_character,
        "style_name": style_row["style_name"],
        "credit": character_row["credit"],
        "param_policy": policy,
        "params": params,
    }


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def validate_lines(
    dialogue: list[dict[str, Any]],
    character_master: dict[str, dict[str, str]],
    voice_style_master: dict[tuple[str, str], dict[str, str]],
    emotion_master: dict[str, dict[str, str]],
) -> None:
    errors: list[str] = []
    seen: set[str] = set()
    if not isinstance(dialogue, list) or not dialogue:
        raise ValueError("dialogue.json は1件以上の行を持つ配列にしてください。")

    for line in dialogue:
        if not isinstance(line, dict):
            errors.append("dialogue.json の各行はオブジェクトにしてください。")
            continue
        for key in ("line_id", "scene_id", "type", "speaker", "emotion", "text", "reading"):
            if not isinstance(line.get(key), str) or not line[key].strip():
                errors.append(f"{key} は空でない文字列にしてください。")
        for key in ("pause_before_sec", "pause_after_sec"):
            try:
                value = float(line.get(key, 0))
                if not math.isfinite(value) or value < 0:
                    raise ValueError
            except (ValueError, TypeError):
                errors.append(f"{line.get('line_id', '?')}: {key} は0以上の有限の秒数にしてください。")
        line_id = str(line.get("line_id", ""))
        speaker = str(line.get("speaker", ""))
        emotion = str(line.get("emotion", ""))
        text = str(line.get("text", ""))
        reading = str(line.get("reading", ""))
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", line_id):
            errors.append(f"{line_id}: line_id は英数字・ハイフン・アンダースコアで指定してください。")
        for key in ("scene_id", "type"):
            if not line.get(key):
                errors.append(f"{line_id}: {key} が空です。")
        if line_id in seen:
            errors.append(f"{line_id}: line_id が重複しています。")
        seen.add(line_id)
        if speaker not in character_master:
            errors.append(f"{line_id}: speaker '{speaker}' が character_master.csv にありません。")
        if emotion not in emotion_master:
            errors.append(f"{line_id}: emotion '{emotion}' が emotion_master.csv にありません。")
        if speaker in character_master and emotion in emotion_master:
            voicevox_character = character_master[speaker]["voicevox_character"]
            if (voicevox_character, emotion) not in voice_style_master:
                errors.append(
                    f"{line_id}: {voicevox_character} / {emotion} が "
                    "voice_style_master.csv にありません。"
                )
        if not text:
            errors.append(f"{line_id}: text が空です。")
        if not reading:
            errors.append(f"{line_id}: reading が空です。")

    if errors:
        raise ValueError("\n".join(errors))


def validate_line_order(line_order: list[str], line_by_id: dict[str, dict[str, Any]]) -> None:
    missing = [line_id for line_id in line_order if line_id not in line_by_id]
    if missing:
        raise ValueError("dialogue.json に存在しない line_id があります: " + ", ".join(missing))


def parse_line_ids(values: list[str] | None) -> list[str]:
    if not values:
        return []

    line_ids: list[str] = []
    for value in values:
        line_ids.extend(part.strip() for part in value.split(",") if part.strip())
    return line_ids


def run(
    project_dir: Path,
    engine_url: str,
    segment_id: str | None = None,
    line_ids: list[str] | None = None,
    check_only: bool = False,
) -> None:
    if segment_id and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", segment_id):
        raise ValueError("segment_id にパスは指定できません。")
    project_dir = project_dir.resolve()
    input_dir = project_dir / "input"
    masters_dir = project_dir / "masters"
    output_dir = project_dir / "output"
    voice_dir = output_dir / "voice"
    metadata_dir = output_dir if segment_id is None else output_dir / "remotion" / segment_id
    selected_line_ids = parse_line_ids(line_ids)

    dialogue: list[dict[str, Any]] = load_json(input_dir / "dialogue.json")
    character_master = load_csv_map(masters_dir / "character_master.csv", "character")
    voice_style_master = load_voice_style_master(masters_dir / "voice_style_master.csv")
    emotion_master = load_csv_map(masters_dir / "emotion_master.csv", "emotion")
    validate_master_contents(character_master, emotion_master)

    validate_lines(dialogue, character_master, voice_style_master, emotion_master)
    line_by_id = {line["line_id"]: line for line in dialogue}
    line_order = build_line_order(project_dir, dialogue, segment_id, selected_line_ids)
    validate_line_order(line_order, line_by_id)
    validate_lines([line_by_id[line_id] for line_id in line_order], character_master, voice_style_master, emotion_master)
    if not line_order:
        raise ValueError("音声生成対象がありません。")
    # Resolve numeric parameters before any network request or output write.
    for line_id in line_order:
        voice = resolve_voice(line_by_id[line_id], character_master, voice_style_master, emotion_master)
        if not all(math.isfinite(value) for value in voice["params"].values()):
            raise ValueError(f"{line_id}: 音声パラメーターに非有限値があります。")
    if check_only:
        print(f"CHECK OK: 音声入力を確認しました。対象 {len(line_order)} 行")
        print("通信・音声生成・出力ファイルの作成や変更は行っていません。")
        print("VOICEVOXの接続・実際の話者・画像・Remotionはこの確認の対象外です。")
        return
    request_json("GET", f"{engine_url.rstrip('/')}/version")
    voice_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    manifest_rows: list[dict[str, Any]] = []
    timeline_rows: list[dict[str, Any]] = []
    credits: set[str] = set()
    current_sec = 0.0

    for line_id in line_order:
        line = line_by_id[line_id]
        voice = resolve_voice(line, character_master, voice_style_master, emotion_master)
        wav_path = voice_dir / f"{line_id}.wav"
        voice_text = line.get("reading") or line["text"]
        synthesize(
            voice_text,
            wav_path,
            speaker=voice["speaker_id"],
            engine_url=engine_url,
            query_overrides=voice["params"],
        )
        audio_sec = wav_duration(wav_path)
        pause_before = float(line.get("pause_before_sec", 0.0))
        pause_after = float(line.get("pause_after_sec", 0.0))
        start_sec = current_sec + pause_before
        end_sec = start_sec + audio_sec
        current_sec = end_sec + pause_after
        credits.add(voice["credit"])

        manifest_rows.append(
            {
                "line_id": line_id,
                "scene_id": line["scene_id"],
                "type": line["type"],
                "speaker": line["speaker"],
                "emotion": line["emotion"],
                "text": line["text"],
                "reading": voice_text,
                "speaker_id": voice["speaker_id"],
                "voicevox_character": voice["voicevox_character"],
                "style_name": voice["style_name"],
                "param_policy": voice["param_policy"],
                "audio_file": str(wav_path.relative_to(project_dir)).replace("\\", "/"),
                "audio_sec": round(audio_sec, 3),
                "credit": voice["credit"],
            }
        )
        timeline_rows.append(
            {
                "scene_id": line["scene_id"],
                "line_id": line_id,
                "type": line["type"],
                "speaker": line["speaker"],
                "audio_file": str(wav_path.relative_to(project_dir)).replace("\\", "/"),
                "audio_sec": round(audio_sec, 3),
                "pause_before_sec": pause_before,
                "pause_after_sec": pause_after,
                "start_sec": round(start_sec, 3),
                "end_sec": round(end_sec, 3),
                "image_file": "",
                "sfx_id": "",
            }
        )
        print(f"{line_id}: {audio_sec:.2f}s -> {wav_path}")

    manifest_name = "voice_manifest_selected.csv" if selected_line_ids else "voice_manifest.csv"
    timeline_name = "timeline_selected.csv" if selected_line_ids else "timeline.csv"

    write_csv(
        metadata_dir / manifest_name,
        manifest_rows,
        [
            "line_id",
            "scene_id",
            "type",
            "speaker",
            "emotion",
            "text",
            "reading",
            "speaker_id",
            "voicevox_character",
            "style_name",
            "param_policy",
            "audio_file",
            "audio_sec",
            "credit",
        ],
    )
    write_csv(
        metadata_dir / timeline_name,
        timeline_rows,
        [
            "scene_id",
            "line_id",
            "type",
            "speaker",
            "audio_file",
            "audio_sec",
            "pause_before_sec",
            "pause_after_sec",
            "start_sec",
            "end_sec",
            "image_file",
            "sfx_id",
        ],
    )
    if not selected_line_ids:
        (metadata_dir / "credits.txt").write_text(
            "音声: " + "、".join(sorted(credits)) + "\n",
            encoding="utf-8",
        )

    if segment_id:
        print(f"対象セグメント: {segment_id}")
    if selected_line_ids:
        print("対象line: " + ", ".join(selected_line_ids))
    print(f"音声ファイル: {len(manifest_rows)}件")
    print(f"合計尺目安: {current_sec:.2f}s")
    print(f"manifest: {metadata_dir / manifest_name}")
    print(f"timeline: {metadata_dir / timeline_name}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create VOICEVOX voice files from literary scenario dialogue.json.")
    parser.add_argument(
        "project_dir",
        type=Path,
    )
    parser.add_argument("--engine-url", default=DEFAULT_ENGINE_URL)
    parser.add_argument("--check", action="store_true", help="音声入力だけ確認する。通信・音声生成・ファイル出力は行わない。")
    parser.add_argument(
        "--segment",
        help="segment_001 のように指定すると、そのセグメントの音声とタイムラインだけを作る。",
    )
    parser.add_argument(
        "--line",
        action="append",
        dest="line_ids",
        help="指定した line_id だけ音声生成する。複数回指定またはカンマ区切り可。",
    )
    args = parser.parse_args()

    try:
        run(args.project_dir, args.engine_url, args.segment, args.line_ids, check_only=args.check)
        return 0
    except (FileNotFoundError, KeyError, ValueError, VoicevoxError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
