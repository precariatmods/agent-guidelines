"""Transcribe an audio file to the meeting-minutes transcript CSV schema."""

from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path


DEFAULT_DOWNLOAD_ROOT = Path(__file__).resolve().parents[1] / ".cache" / "whisper"

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "音声全体を faster-whisper で文字起こしし、"
            "transcript.csv 形式で保存します。"
        )
    )
    parser.add_argument("input", type=Path, help="入力音声または動画のパス")
    parser.add_argument("output", type=Path, help="出力する transcript.csv のパス")
    parser.add_argument(
        "--model",
        default="small",
        help="Whisperモデル名またはローカルモデルのパス（既定: small）",
    )
    parser.add_argument("--language", default="ja", help="言語コード（既定: ja）")
    parser.add_argument("--device", default="cpu", help="実行デバイス（既定: cpu）")
    parser.add_argument(
        "--compute-type",
        default="int8",
        help="計算精度（既定: int8）",
    )
    parser.add_argument(
        "--beam-size",
        type=int,
        default=5,
        help="ビームサイズ（既定: 5）",
    )
    parser.add_argument(
        "--speaker-id",
        default="speaker_001",
        help="全行へ設定する仮話者ID（既定: speaker_001）",
    )
    parser.add_argument(
        "--download-root",
        type=Path,
        default=DEFAULT_DOWNLOAD_ROOT,
        help="モデルの保存先（既定: meeting-minutes/.cache/whisper）",
    )
    parser.add_argument(
        "--initial-prompt",
        help="固有名詞などを補助する初期プロンプト",
    )
    parser.add_argument(
        "--vad-filter",
        action="store_true",
        help="無音区間をVADで除外する",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="既存の出力ファイルを上書きする",
    )
    return parser.parse_args()


def format_timestamp(seconds: float) -> str:
    total_milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(total_milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, milliseconds = divmod(remainder, 1_000)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d}.{milliseconds:03d}"


def validate_args(args: argparse.Namespace) -> None:
    args.input = args.input.resolve()
    args.output = args.output.resolve()

    if not args.input.is_file():
        raise ValueError(f"入力ファイルが見つかりません: {args.input}")
    if args.input == args.output:
        raise ValueError("入力ファイルと出力ファイルに同じパスは指定できません。")
    if args.output.exists() and not args.force:
        raise FileExistsError(
            f"出力ファイルは既に存在します: {args.output}\n"
            "上書きする場合は --force を指定してください。"
        )
    if args.beam_size < 1:
        raise ValueError("--beam-size は1以上にしてください。")
    if not args.speaker_id.strip():
        raise ValueError("--speaker-id は空にできません。")


def transcribe(args: argparse.Namespace) -> int:
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "faster-whisper が見つかりません。"
            "`python -m pip install -r scripts/requirements.txt`を実行してください。"
        ) from exc

    model_kwargs: dict[str, object] = {
        "device": args.device,
        "compute_type": args.compute_type,
    }
    if args.download_root:
        model_kwargs["download_root"] = str(args.download_root.resolve())

    print(f"入力: {args.input}", file=sys.stderr)
    print(f"出力: {args.output}", file=sys.stderr)
    print(f"モデル: {args.model}", file=sys.stderr)

    model = WhisperModel(args.model, **model_kwargs)
    segments, info = model.transcribe(
        str(args.input),
        language=args.language,
        beam_size=args.beam_size,
        vad_filter=args.vad_filter,
        condition_on_previous_text=True,
        initial_prompt=args.initial_prompt,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = args.output.with_name(f".{args.output.name}.tmp")
    row_count = 0

    try:
        with temporary_output.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\r\n")
            writer.writerow(["line_id", "speaker_id", "start_time", "end_time", "text"])

            for segment in segments:
                text = segment.text.strip().replace("\r", " ").replace("\n", " ")
                if not text:
                    continue
                row_count += 1
                writer.writerow(
                    [
                        f"line_{row_count:06d}",
                        args.speaker_id,
                        format_timestamp(segment.start),
                        format_timestamp(segment.end),
                        text,
                    ]
                )
                print(
                    f"{format_timestamp(segment.start)} "
                    f"{format_timestamp(segment.end)} {text}",
                    file=sys.stderr,
                )

        os.replace(temporary_output, args.output)
    except BaseException:
        temporary_output.unlink(missing_ok=True)
        raise

    print(
        f"完了: {row_count}行 / 検出言語={info.language} / "
        f"音声長={info.duration:.2f}秒",
        file=sys.stderr,
    )
    return row_count


def main() -> int:
    args = parse_args()
    try:
        validate_args(args)
        transcribe(args)
    except (FileExistsError, RuntimeError, ValueError) as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("中断しました。", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
