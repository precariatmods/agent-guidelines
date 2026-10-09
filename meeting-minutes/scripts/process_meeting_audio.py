"""Run transcription, speaker diarization, and person-master linking."""

from __future__ import annotations

import argparse
import os
import sys
from argparse import Namespace
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CACHE_ROOT = PROJECT_ROOT / ".cache"
os.environ.setdefault("WHISPER_MODEL_DIR", str(CACHE_ROOT / "whisper"))
os.environ.setdefault("SPEAKER_MODEL_DIR", str(CACHE_ROOT / "speaker-models"))

import check_python_components
import link_speakers
import transcribe_audio


DEFAULT_WHISPER_MODEL = "small"
DEFAULT_SPEAKER_MODEL = "3dspeaker_speech_campplus_sv_zh-cn_16k-common.onnx"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "音声の文字起こし、話者パターン分離、人物マスターとの紐付けを"
            "一括して実行します。"
        )
    )
    parser.add_argument("audio", type=Path, help="入力音声または動画")
    parser.add_argument("person_master", type=Path, help="人物マスターCSV")
    parser.add_argument("work_dir", type=Path, help="中間CSVの保存フォルダ")
    parser.add_argument(
        "--num-speakers",
        type=int,
        help="音声に含まれる人数が確実な場合だけ指定する",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="人物選択を行わず、仮話者IDと候補CSVだけを出力する",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="既存の生成ファイルを上書きする",
    )
    parser.add_argument(
        "--reuse-transcript",
        action="store_true",
        help="既存の全文文字起こしが同じ音声のものだと確認済みの場合だけ再利用する",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    args.audio = args.audio.resolve()
    args.person_master = args.person_master.resolve()
    args.work_dir = args.work_dir.resolve()

    if not args.audio.is_file():
        raise ValueError(f"入力音声が見つかりません: {args.audio}")
    if not args.person_master.is_file():
        raise ValueError(f"人物マスターが見つかりません: {args.person_master}")
    if args.num_speakers is not None and args.num_speakers < 1:
        raise ValueError("--num-speakersは1以上にしてください。")


def build_paths(work_dir: Path) -> dict[str, Path]:
    return {
        "raw": work_dir / "transcript_raw.csv",
        "linked": work_dir / "transcript.csv",
        "candidates": work_dir / "speaker_candidates.csv",
    }


def run_transcription(args: argparse.Namespace, raw_output: Path) -> None:
    if raw_output.exists() and not args.force:
        if args.reuse_transcript:
            print(f"確認済みの文字起こしを再利用: {raw_output}", file=sys.stderr)
            return
        raise FileExistsError(
            f"既存の文字起こしがあります: {raw_output}\n"
            "同じ音声のものと確認済みなら--reuse-transcript、"
            "作り直す場合は--forceを指定してください。"
        )

    transcription_args = Namespace(
        input=args.audio,
        output=raw_output,
        model=os.environ.get("WHISPER_MODEL", DEFAULT_WHISPER_MODEL),
        language="ja",
        device="cpu",
        compute_type="int8",
        beam_size=5,
        speaker_id="speaker_001",
        download_root=(
            Path(os.environ["WHISPER_MODEL_DIR"])
            if os.environ.get("WHISPER_MODEL_DIR")
            else None
        ),
        initial_prompt=None,
        vad_filter=False,
        force=args.force,
    )
    transcribe_audio.validate_args(transcription_args)
    transcribe_audio.transcribe(transcription_args)


def run_speaker_linking(
    args: argparse.Namespace,
    paths: dict[str, Path],
) -> None:
    mapping = paths["candidates"] if paths["candidates"].is_file() else None
    interactive = not args.non_interactive and sys.stdin.isatty()

    if not interactive and not args.non_interactive:
        print(
            "対話入力を利用できないため、人物を確定せず候補CSVを出力します。",
            file=sys.stderr,
        )

    output_exists = paths["linked"].exists() or paths["candidates"].exists()
    if output_exists and not args.force:
        raise FileExistsError(
            "話者分離の出力が既に存在します。内容を確認し、"
            "再実行する場合は--forceを指定してください。"
        )

    linking_args = Namespace(
        audio=args.audio,
        transcript=paths["raw"],
        person_master=args.person_master,
        output=paths["linked"],
        candidates_output=paths["candidates"],
        mapping=mapping,
        interactive=interactive,
        speaker_model=(
            Path(os.environ.get("SPEAKER_MODEL_DIR", CACHE_ROOT / "speaker-models"))
            / DEFAULT_SPEAKER_MODEL
        ),
        cluster_threshold=0.65,
        num_speakers=args.num_speakers,
        force=args.force,
    )
    link_speakers.validate_args(linking_args)
    link_speakers.process(linking_args)


def print_summary(paths: dict[str, Path]) -> None:
    print("\n生成ファイル:", file=sys.stderr)
    print(f"  文字起こし: {paths['raw']}", file=sys.stderr)
    print(f"  話者パターン: {paths['candidates']}", file=sys.stderr)
    print(f"  人物紐付け後: {paths['linked']}", file=sys.stderr)


def main() -> int:
    args = parse_args()
    try:
        validate_args(args)
        paths = build_paths(args.work_dir)
        args.work_dir.mkdir(parents=True, exist_ok=True)
        script_dir = Path(__file__).resolve().parent
        check_python_components.ensure_components(script_dir / "requirements.txt")
        print(f"入力音声: {args.audio}", file=sys.stderr)
        print(f"人物マスター: {args.person_master}", file=sys.stderr)
        print(f"作業フォルダ: {args.work_dir}", file=sys.stderr)
        run_transcription(args, paths["raw"])
        run_speaker_linking(args, paths)
        print_summary(paths)
    except (FileExistsError, RuntimeError, ValueError) as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("中断しました。", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
