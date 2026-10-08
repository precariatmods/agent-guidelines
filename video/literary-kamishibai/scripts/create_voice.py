from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


CSV_CHARACTER = "シナリオ登場キャラ名"
CSV_VOICEVOX_NAME = "VoiceVOXキャラ名"
CSV_VOICEVOX_ID = "VoiceVOXキャラID"
REQUIRED_LINE_KEYS = ("line_id", "scene_id", "image", "character", "text")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def load_dialogue(path: Path) -> list[dict[str, str]]:
    data: Any = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, list) or not data:
        raise ValueError("dialogue.jsonは1件以上の配列にしてください。")

    result: list[dict[str, str]] = []
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
            raise ValueError(f"{line['line_id']}: line_idは英数字、_、-だけにしてください。")
        if line["line_id"] in seen:
            raise ValueError(f"{line['line_id']}: line_idが重複しています。")
        seen.add(line["line_id"])
        result.append(line)
    return result


def load_characters(path: Path) -> dict[str, tuple[str, int]]:
    result: dict[str, tuple[str, int]] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        expected = {CSV_CHARACTER, CSV_VOICEVOX_NAME, CSV_VOICEVOX_ID}
        if set(reader.fieldnames or []) != expected:
            raise ValueError("voicevox_characters.csvの列は指定された3列だけにしてください。")
        for row_number, row in enumerate(reader, start=2):
            character = (row.get(CSV_CHARACTER) or "").strip()
            voicevox_name = (row.get(CSV_VOICEVOX_NAME) or "").strip()
            raw_id = (row.get(CSV_VOICEVOX_ID) or "").strip()
            if not character or not voicevox_name or not raw_id:
                raise ValueError(f"voicevox_characters.csvの{row_number}行目に空欄があります。")
            try:
                speaker_id = int(raw_id)
            except ValueError as exc:
                raise ValueError(f"{row_number}行目のVoiceVOXキャラIDは整数ではありません。") from exc
            if speaker_id < 0:
                raise ValueError(f"{row_number}行目のVoiceVOXキャラIDは0以上にしてください。")
            if character in result:
                raise ValueError(f"{character}: 配役が重複しています。")
            result[character] = (voicevox_name, speaker_id)
    if not result:
        raise ValueError("voicevox_characters.csvに配役がありません。")
    return result


def request(url: str, method: str = "GET", body: bytes | None = None) -> bytes:
    headers = {"Content-Type": "application/json"} if body is not None else {}
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return response.read()
    except urllib.error.URLError as exc:
        raise RuntimeError(f"VOICEVOX Engineへ接続できません: {exc}") from exc


def synthesize(engine_url: str, text: str, speaker_id: int) -> bytes:
    query_string = urllib.parse.urlencode({"text": text, "speaker": speaker_id})
    audio_query = request(
        f"{engine_url}/audio_query?{query_string}", method="POST", body=b""
    )
    synthesis_query = urllib.parse.urlencode({"speaker": speaker_id})
    return request(
        f"{engine_url}/synthesis?{synthesis_query}", method="POST", body=audio_query
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="dialogue.jsonからVOICEVOX音声を作成します。")
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--engine-url", default="http://127.0.0.1:50021")
    args = parser.parse_args()

    try:
        project_dir = args.project_dir.resolve()
        dialogue = load_dialogue(project_dir / "dialogue.json")
        characters = load_characters(project_dir / "voicevox_characters.csv")
        missing = sorted({line["character"] for line in dialogue} - set(characters))
        if missing:
            raise ValueError("配役がありません: " + ", ".join(missing))

        engine_url = args.engine_url.rstrip("/")
        version = request(f"{engine_url}/version").decode("utf-8").strip().strip('"')
        print(f"VOICEVOX Engine: {version}")

        audio_dir = project_dir / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)
        for line in dialogue:
            voicevox_name, speaker_id = characters[line["character"]]
            wav = synthesize(engine_url, line["text"], speaker_id)
            output = audio_dir / f"{line['line_id']}.wav"
            output.write_bytes(wav)
            print(f"{line['line_id']}.wav: {line['character']} / {voicevox_name} / ID {speaker_id}")
        return 0
    except (FileNotFoundError, json.JSONDecodeError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
