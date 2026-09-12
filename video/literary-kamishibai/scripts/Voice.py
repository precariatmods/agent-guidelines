from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_ENGINE_URL = "http://localhost:50021"
DEFAULT_SPEAKER = 3
DEFAULT_TEXT = "こんにちは。VOICEVOX APIから音声を作成しました。"


class VoicevoxError(RuntimeError):
    pass


def request_json(
    method: str,
    url: str,
    *,
    params: dict[str, Any] | None = None,
    body: Any | None = None,
) -> Any:
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"

    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise VoicevoxError(f"{method} {url} failed: HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise VoicevoxError(f"Could not connect to VoiceVOX Engine at {url}: {exc}") from exc


def request_bytes(
    method: str,
    url: str,
    *,
    params: dict[str, Any] | None = None,
    body: Any | None = None,
) -> bytes:
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"

    data = None
    headers = {"Accept": "audio/wav"}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise VoicevoxError(f"{method} {url} failed: HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise VoicevoxError(f"Could not connect to VoiceVOX Engine at {url}: {exc}") from exc


def synthesize(
    text: str,
    output: Path,
    *,
    speaker: int = DEFAULT_SPEAKER,
    engine_url: str = DEFAULT_ENGINE_URL,
    speed: float | None = None,
    pitch: float | None = None,
    intonation: float | None = None,
    volume: float | None = None,
    pre_phoneme_length: float | None = None,
    post_phoneme_length: float | None = None,
    pause_length_scale: float | None = None,
    query_overrides: dict[str, Any] | None = None,
    accent_overrides: dict[str, Any] | None = None,
) -> None:
    engine_url = engine_url.rstrip("/")
    query = request_json(
        "POST",
        f"{engine_url}/audio_query",
        params={"text": text, "speaker": speaker},
    )

    if speed is not None:
        query["speedScale"] = speed
    if pitch is not None:
        query["pitchScale"] = pitch
    if intonation is not None:
        query["intonationScale"] = intonation
    if volume is not None:
        query["volumeScale"] = volume
    if pre_phoneme_length is not None:
        query["prePhonemeLength"] = pre_phoneme_length
    if post_phoneme_length is not None:
        query["postPhonemeLength"] = post_phoneme_length
    if pause_length_scale is not None:
        query["pauseLengthScale"] = pause_length_scale
    if query_overrides:
        query.update(query_overrides)
    if accent_overrides:
        apply_accent_overrides(query, accent_overrides)

    wav = request_bytes(
        "POST",
        f"{engine_url}/synthesis",
        params={"speaker": speaker},
        body=query,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(wav)


def apply_accent_overrides(query: dict[str, Any], overrides: dict[str, Any]) -> None:
    phrases = query.get("accent_phrases", [])

    for phrase_index, accent in overrides.get("phrase_accents", {}).items():
        index = int(phrase_index)
        if 0 <= index < len(phrases):
            phrases[index]["accent"] = int(accent)

    pitch_scale = overrides.get("pitch_scale")
    pitch_shift = overrides.get("pitch_shift")
    vowel_length_scale = overrides.get("vowel_length_scale")
    consonant_length_scale = overrides.get("consonant_length_scale")

    for phrase in phrases:
        for mora in phrase.get("moras", []):
            if pitch_scale is not None:
                mora["pitch"] = mora.get("pitch", 0.0) * float(pitch_scale)
            if pitch_shift is not None:
                mora["pitch"] = mora.get("pitch", 0.0) + float(pitch_shift)
            if vowel_length_scale is not None and mora.get("vowel_length") is not None:
                mora["vowel_length"] *= float(vowel_length_scale)
            if consonant_length_scale is not None and mora.get("consonant_length") is not None:
                mora["consonant_length"] *= float(consonant_length_scale)

    for mora_edit in overrides.get("mora_edits", []):
        phrase_index = int(mora_edit["phrase"])
        mora_index = int(mora_edit["mora"])
        if not 0 <= phrase_index < len(phrases):
            continue
        moras = phrases[phrase_index].get("moras", [])
        if not 0 <= mora_index < len(moras):
            continue
        moras[mora_index].update(
            {key: value for key, value in mora_edit.items() if key not in {"phrase", "mora"}}
        )

    for phrase_edit in overrides.get("phrase_edits", []):
        phrase_index = int(phrase_edit["phrase"])
        if not 0 <= phrase_index < len(phrases):
            continue
        phrase = phrases[phrase_index]
        if "accent" in phrase_edit:
            phrase["accent"] = int(phrase_edit["accent"])
        if "pause_mora" in phrase_edit:
            phrase["pause_mora"] = phrase_edit["pause_mora"]


def list_speakers(engine_url: str = DEFAULT_ENGINE_URL) -> None:
    speakers = request_json("GET", f"{engine_url.rstrip('/')}/speakers")
    for speaker in speakers:
        print(speaker["name"])
        for style in speaker["styles"]:
            print(f"  {style['id']:>3}  {style['name']} ({style.get('type', 'talk')})")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Small VoiceVOX Engine API client.")
    parser.add_argument("--engine-url", default=DEFAULT_ENGINE_URL)

    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("speakers", help="List available speaker style IDs.")

    synth = subparsers.add_parser("synth", help="Synthesize text to a WAV file.")
    synth.add_argument("text", nargs="?", default=DEFAULT_TEXT)
    synth.add_argument("-o", "--output", default="voicevox_output.wav")
    synth.add_argument("-s", "--speaker", type=int, default=DEFAULT_SPEAKER)
    synth.add_argument("--speed", type=float)
    synth.add_argument("--pitch", type=float)
    synth.add_argument("--intonation", type=float)
    synth.add_argument("--volume", type=float)
    synth.add_argument("--pre-phoneme-length", type=float)
    synth.add_argument("--post-phoneme-length", type=float)
    synth.add_argument("--pause-length-scale", type=float)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "speakers":
            list_speakers(args.engine_url)
            return 0

        output = Path(getattr(args, "output", "voicevox_output.wav"))
        synthesize(
            getattr(args, "text", DEFAULT_TEXT),
            output,
            speaker=getattr(args, "speaker", DEFAULT_SPEAKER),
            engine_url=args.engine_url,
            speed=getattr(args, "speed", None),
            pitch=getattr(args, "pitch", None),
            intonation=getattr(args, "intonation", None),
            volume=getattr(args, "volume", None),
            pre_phoneme_length=getattr(args, "pre_phoneme_length", None),
            post_phoneme_length=getattr(args, "post_phoneme_length", None),
            pause_length_scale=getattr(args, "pause_length_scale", None),
        )
        print(f"Wrote {output.resolve()}")
        return 0
    except VoicevoxError as exc:
        print(exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
