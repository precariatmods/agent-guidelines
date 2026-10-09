"""Diarize audio and link transcript speakers to a confirmed person master."""

from __future__ import annotations

import argparse
import csv
import os
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


TRANSCRIPT_COLUMNS = ["line_id", "speaker_id", "start_time", "end_time", "text"]
PERSON_COLUMNS = ["ID", "name", "Department", "Email"]
CANDIDATE_COLUMNS = [
    "diarization_speaker_id",
    "speaker_id",
    "person_id",
    "name",
    "department",
    "confirmation_status",
    "total_seconds",
    "sample_text",
]


@dataclass(frozen=True)
class SpeakerTurn:
    start: float
    end: float
    label: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "公開ONNXモデルで声の特徴を分類し、文字起こしの話者IDを"
            "人物マスターのIDへ確認付きで紐付けます。"
        )
    )
    parser.add_argument("audio", type=Path, help="元音声または動画のパス")
    parser.add_argument("transcript", type=Path, help="紐付け前の文字起こしCSV")
    parser.add_argument("person_master", type=Path, help="人物マスターCSV")
    parser.add_argument("output", type=Path, help="紐付け後の文字起こしCSV")
    parser.add_argument(
        "--candidates-output",
        type=Path,
        help="話者候補CSVの保存先（既定: outputと同じフォルダ）",
    )
    parser.add_argument(
        "--mapping",
        type=Path,
        help=(
            "確認済み対応表CSV。"
            "diarization_speaker_idとperson_id列を使用します"
        ),
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="話者ごとに人物IDを対話入力する",
    )
    parser.add_argument("--speaker-model", type=Path, required=True, help="話者特徴抽出ONNXモデル")
    parser.add_argument(
        "--cluster-threshold",
        type=float,
        default=0.65,
        help="同一話者とみなすコサイン類似度（既定: 0.65）",
    )
    parser.add_argument("--num-speakers", type=int, help="話者数を固定する")
    parser.add_argument("--force", action="store_true", help="既存の出力を上書きする")
    return parser.parse_args()


def parse_timestamp(value: str) -> float:
    try:
        hours_text, minutes_text, seconds_text = value.split(":")
        hours = int(hours_text)
        minutes = int(minutes_text)
        seconds = float(seconds_text)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"時刻形式が不正です: {value}") from exc
    if hours < 0 or not 0 <= minutes < 60 or not 0 <= seconds < 60:
        raise ValueError(f"時刻範囲が不正です: {value}")
    return hours * 3600 + minutes * 60 + seconds


def read_csv(path: Path, required_columns: list[str]) -> list[dict[str, str]]:
    last_error: UnicodeDecodeError | None = None
    for encoding in ("utf-8-sig", "cp932"):
        try:
            with path.open("r", encoding=encoding, newline="") as stream:
                reader = csv.DictReader(stream)
                headers = reader.fieldnames or []
                missing = [column for column in required_columns if column not in headers]
                if missing:
                    raise ValueError(
                        f"{path}に必要な列がありません: {', '.join(missing)}"
                    )
                return [dict(row) for row in reader]
        except UnicodeDecodeError as exc:
            last_error = exc
    if last_error:
        raise ValueError(f"{path}をUTF-8またはCP932として読み込めません。") from last_error
    raise ValueError(f"{path}を読み込めません。")


def read_transcript(path: Path) -> list[dict[str, str]]:
    rows = read_csv(path, TRANSCRIPT_COLUMNS)
    line_ids: set[str] = set()
    previous_start = -1.0
    for row in rows:
        line_id = row["line_id"]
        if not line_id or line_id in line_ids:
            raise ValueError(f"line_idが空欄または重複しています: {line_id}")
        line_ids.add(line_id)
        start = parse_timestamp(row["start_time"])
        end = parse_timestamp(row["end_time"])
        if end <= start:
            raise ValueError(f"end_timeがstart_time以前です: {line_id}")
        if start < previous_start:
            raise ValueError("文字起こしがstart_timeの昇順ではありません。")
        previous_start = start
    return rows


def read_people(path: Path) -> dict[str, dict[str, str]]:
    rows = read_csv(path, PERSON_COLUMNS)
    people: dict[str, dict[str, str]] = {}
    for row in rows:
        person_id = row["ID"].strip()
        if not person_id:
            continue
        if person_id in people:
            raise ValueError(f"人物マスターでIDが重複しています: {person_id}")
        people[person_id] = row
    if not people:
        raise ValueError("人物マスターにID付きのデータ行がありません。")
    return people


def read_mapping(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    rows = read_csv(path, ["diarization_speaker_id", "person_id"])
    mapping: dict[str, str] = {}
    for row in rows:
        label = row["diarization_speaker_id"].strip()
        person_id = row["person_id"].strip()
        if not label or not person_id:
            continue
        if label in mapping and mapping[label] != person_id:
            raise ValueError(f"対応表で話者が重複しています: {label}")
        mapping[label] = person_id
    return mapping


def load_audio(path: Path, sample_rate: int = 16_000):
    try:
        import av
        import numpy as np
    except ImportError as exc:
        raise RuntimeError(
            "音声読み込みに必要なパッケージが見つかりません。"
            "`python -m pip install -r scripts/requirements.txt`を実行してください。"
        ) from exc
    chunks = []
    with av.open(str(path)) as container:
        stream = next((item for item in container.streams if item.type == "audio"), None)
        if stream is None:
            raise RuntimeError("音声ストリームが見つかりませんでした。")
        resampler = av.AudioResampler(format="fltp", layout="mono", rate=sample_rate)
        for frame in container.decode(stream):
            for converted in resampler.resample(frame):
                chunks.append(converted.to_ndarray().reshape(-1).astype("float32"))
        for converted in resampler.resample(None):
            chunks.append(converted.to_ndarray().reshape(-1).astype("float32"))
    if not chunks:
        raise RuntimeError("音声データを読み込めませんでした。")
    return np.ascontiguousarray(np.concatenate(chunks)), sample_rate


def cluster_embeddings(embeddings, num_speakers: int | None, threshold: float):
    import numpy as np

    matrix = np.asarray(embeddings, dtype="float32")
    matrix /= np.maximum(np.linalg.norm(matrix, axis=1, keepdims=True), 1e-8)
    if num_speakers:
        count = min(num_speakers, len(matrix))
        seeds = [0]
        while len(seeds) < count:
            similarities = matrix @ matrix[seeds].T
            seeds.append(int(np.argmin(np.max(similarities, axis=1))))
        centroids = matrix[seeds].copy()
        labels = np.full(len(matrix), -1, dtype=int)
        for _ in range(20):
            updated = np.argmax(matrix @ centroids.T, axis=1)
            if np.array_equal(labels, updated):
                break
            labels = updated
            for index in range(count):
                members = matrix[labels == index]
                if len(members):
                    centroid = members.mean(axis=0)
                    centroids[index] = centroid / max(np.linalg.norm(centroid), 1e-8)
        return labels.tolist()

    centroids = []
    counts = []
    labels = []
    for embedding in matrix:
        if not centroids:
            centroids.append(embedding.copy())
            counts.append(1)
            labels.append(0)
            continue
        similarities = np.asarray(centroids) @ embedding
        best = int(np.argmax(similarities))
        if float(similarities[best]) < threshold:
            centroids.append(embedding.copy())
            counts.append(1)
            labels.append(len(centroids) - 1)
            continue
        counts[best] += 1
        centroid = centroids[best] + (embedding - centroids[best]) / counts[best]
        centroids[best] = centroid / max(np.linalg.norm(centroid), 1e-8)
        labels.append(best)
    return labels


def run_diarization(
    args: argparse.Namespace,
    transcript: list[dict[str, str]],
) -> list[SpeakerTurn]:
    try:
        import numpy as np
        import sherpa_onnx
    except ImportError as exc:
        raise RuntimeError(
            "sherpa-onnxが見つかりません。"
            "`python -m pip install -r scripts/requirements.txt`を実行してください。"
        ) from exc

    if not args.speaker_model.is_file():
        raise RuntimeError(f"話者特徴モデルが見つかりません: {args.speaker_model}")
    config = sherpa_onnx.SpeakerEmbeddingExtractorConfig(
        model=str(args.speaker_model), num_threads=2, provider="cpu"
    )
    if not config.validate():
        raise RuntimeError(f"話者特徴モデルの設定が不正です: {args.speaker_model}")
    extractor = sherpa_onnx.SpeakerEmbeddingExtractor(config)
    audio, sample_rate = load_audio(args.audio)
    embeddings = []
    valid_rows = []
    for index, row in enumerate(transcript):
        start = parse_timestamp(row["start_time"])
        end = parse_timestamp(row["end_time"])
        if end - start < 1.0:
            center = (start + end) / 2
            start = max(0.0, center - 0.5)
            end = min(len(audio) / sample_rate, center + 0.5)
        samples = np.ascontiguousarray(
            audio[int(start * sample_rate) : int(end * sample_rate)],
            dtype="float32",
        )
        stream = extractor.create_stream()
        stream.accept_waveform(sample_rate=sample_rate, waveform=samples)
        stream.input_finished()
        if not extractor.is_ready(stream):
            continue
        embeddings.append(np.asarray(extractor.compute(stream), dtype="float32"))
        valid_rows.append(index)
    if not embeddings:
        raise RuntimeError("声の特徴を抽出できる発言区間がありませんでした。")

    cluster_ids = cluster_embeddings(
        embeddings, args.num_speakers, args.cluster_threshold
    )
    row_labels = ["UNASSIGNED"] * len(transcript)
    for row_index, cluster_id in zip(valid_rows, cluster_ids, strict=True):
        row_labels[row_index] = f"voice_{cluster_id:03d}"
    return [
        SpeakerTurn(
            parse_timestamp(row["start_time"]),
            parse_timestamp(row["end_time"]),
            label,
        )
        for row, label in zip(transcript, row_labels, strict=True)
    ]


def ordered_labels(turns: Iterable[SpeakerTurn]) -> list[str]:
    first_start: dict[str, float] = {}
    for turn in turns:
        first_start.setdefault(turn.label, turn.start)
    return sorted(first_start, key=lambda label: (first_start[label], label))


def select_speaker(start: float, end: float, turns: list[SpeakerTurn]) -> str | None:
    overlap_by_speaker: dict[str, float] = defaultdict(float)
    for turn in turns:
        if turn.end <= start:
            continue
        if turn.start >= end:
            break
        overlap = max(0.0, min(end, turn.end) - max(start, turn.start))
        overlap_by_speaker[turn.label] += overlap
    if not overlap_by_speaker:
        return None
    return max(overlap_by_speaker, key=lambda label: overlap_by_speaker[label])


def collect_samples(
    transcript: list[dict[str, str]],
    assigned_labels: list[str],
    max_samples: int = 3,
) -> dict[str, list[str]]:
    samples: dict[str, list[str]] = defaultdict(list)
    for row, label in zip(transcript, assigned_labels, strict=True):
        text = row["text"].strip()
        if text and len(samples[label]) < max_samples:
            samples[label].append(text)
    return samples


def interactive_mapping(
    labels: list[str],
    people: dict[str, dict[str, str]],
    samples: dict[str, list[str]],
    existing: dict[str, str],
) -> dict[str, str]:
    if not sys.stdin.isatty():
        raise ValueError("--interactiveは対話可能なターミナルで実行してください。")

    print("\n人物候補:", file=sys.stderr)
    for person_id, row in people.items():
        print(
            f"  {person_id}: {row['name']}（{row['Department']}）",
            file=sys.stderr,
        )

    mapping = dict(existing)
    display_number = 0
    for label in labels:
        if label == "UNASSIGNED" or label in mapping:
            continue
        display_number += 1
        print(f"\nパターン{display_number}（{label}）の発言例:", file=sys.stderr)
        for sample in samples.get(label, []):
            print(f"  - {sample}", file=sys.stderr)
        while True:
            person_id = input(
                f"パターン{display_number}に対応する人物ID（未確定は空欄）: "
            ).strip()
            if not person_id:
                break
            if person_id in people:
                person = people[person_id]
                answer = input(
                    f"{label}は{person['name']}（{person['Department']}）で"
                    "よいですか？ [y/N]: "
                ).strip()
                if answer.casefold() in {"y", "yes"}:
                    mapping[label] = person_id
                    print(
                        f"確認: {label} -> {person_id} {person['name']}",
                        file=sys.stderr,
                    )
                    break
                print("人物を選び直してください。", file=sys.stderr)
                continue
            print("人物マスターに存在する人物IDを入力してください。", file=sys.stderr)
    return mapping


def validate_mapping(
    mapping: dict[str, str],
    labels: list[str],
    people: dict[str, dict[str, str]],
) -> None:
    unknown_labels = sorted(set(mapping) - set(labels))
    if unknown_labels:
        raise ValueError(
            "対応表に音声で検出されていない話者があります: "
            + ", ".join(unknown_labels)
        )
    unknown_people = sorted(set(mapping.values()) - set(people))
    if unknown_people:
        raise ValueError(
            "対応表の人物IDが人物マスターにありません: " + ", ".join(unknown_people)
        )


def write_csv(path: Path, columns: list[str], rows: list[dict[str, object]]) -> Path:
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)
    return temporary


def validate_args(args: argparse.Namespace) -> None:
    args.audio = args.audio.resolve()
    args.transcript = args.transcript.resolve()
    args.person_master = args.person_master.resolve()
    args.output = args.output.resolve()
    args.candidates_output = (
        args.candidates_output.resolve()
        if args.candidates_output
        else args.output.with_name("speaker_candidates.csv")
    )
    if args.mapping:
        args.mapping = args.mapping.resolve()
    args.speaker_model = args.speaker_model.resolve()

    for path, label in (
        (args.audio, "音声"),
        (args.transcript, "文字起こし"),
        (args.person_master, "人物マスター"),
    ):
        if not path.is_file():
            raise ValueError(f"{label}が見つかりません: {path}")
    if args.mapping and not args.mapping.is_file():
        raise ValueError(f"対応表が見つかりません: {args.mapping}")
    if args.output == args.transcript:
        raise ValueError("紐付け前と紐付け後の文字起こしは別パスにしてください。")
    if args.output == args.candidates_output:
        raise ValueError("文字起こしと話者候補CSVは別パスにしてください。")
    if args.num_speakers is not None and args.num_speakers < 1:
        raise ValueError("--num-speakersは1以上にしてください。")
    if not 0.0 < args.cluster_threshold <= 1.0:
        raise ValueError("--cluster-thresholdは0より大きく1以下にしてください。")
    for path in (args.output, args.candidates_output):
        if path.exists() and not args.force:
            raise FileExistsError(
                f"出力ファイルは既に存在します: {path}\n"
                "上書きする場合は--forceを指定してください。"
            )


def process(args: argparse.Namespace) -> tuple[int, int]:
    transcript = read_transcript(args.transcript)
    people = read_people(args.person_master)
    turns = run_diarization(args, transcript)
    labels = ordered_labels(turns)

    unassigned_label = "UNASSIGNED"
    assigned_labels: list[str] = []
    for row in transcript:
        label = select_speaker(
            parse_timestamp(row["start_time"]),
            parse_timestamp(row["end_time"]),
            turns,
        )
        assigned_labels.append(label or unassigned_label)
    if unassigned_label in assigned_labels:
        labels.append(unassigned_label)

    samples = collect_samples(transcript, assigned_labels)
    mapping = read_mapping(args.mapping)
    if args.interactive:
        mapping = interactive_mapping(labels, people, samples, mapping)
    validate_mapping(mapping, labels, people)

    temporary_ids = {
        label: f"speaker_{index:03d}" for index, label in enumerate(labels, start=1)
    }
    linked_rows: list[dict[str, object]] = []
    for row, label in zip(transcript, assigned_labels, strict=True):
        output_row: dict[str, object] = dict(row)
        person_id = mapping.get(label)
        output_row["speaker_id"] = (
            f"person:{person_id}" if person_id else temporary_ids[label]
        )
        linked_rows.append(output_row)

    total_seconds: dict[str, float] = defaultdict(float)
    for turn in turns:
        total_seconds[turn.label] += turn.end - turn.start

    candidate_rows: list[dict[str, object]] = []
    for label in labels:
        person_id = mapping.get(label, "")
        person = people.get(person_id, {})
        candidate_rows.append(
            {
                "diarization_speaker_id": label,
                "speaker_id": (
                    f"person:{person_id}" if person_id else temporary_ids[label]
                ),
                "person_id": person_id,
                "name": person.get("name", ""),
                "department": person.get("Department", ""),
                "confirmation_status": "確認済み" if person_id else "未確認",
                "total_seconds": f"{total_seconds.get(label, 0.0):.3f}",
                "sample_text": " / ".join(samples.get(label, [])),
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.candidates_output.parent.mkdir(parents=True, exist_ok=True)
    linked_temporary = write_csv(args.output, TRANSCRIPT_COLUMNS, linked_rows)
    candidates_temporary = write_csv(
        args.candidates_output, CANDIDATE_COLUMNS, candidate_rows
    )
    try:
        os.replace(linked_temporary, args.output)
        os.replace(candidates_temporary, args.candidates_output)
    except BaseException:
        linked_temporary.unlink(missing_ok=True)
        candidates_temporary.unlink(missing_ok=True)
        raise

    confirmed = sum(1 for label in labels if label in mapping)
    print(f"検出話者: {len(labels)}", file=sys.stderr)
    print(f"参加者へ確認済み: {confirmed}", file=sys.stderr)
    print(f"文字起こし出力: {args.output}", file=sys.stderr)
    print(f"話者候補出力: {args.candidates_output}", file=sys.stderr)
    return len(labels), confirmed


def main() -> int:
    args = parse_args()
    try:
        validate_args(args)
        process(args)
    except (FileExistsError, RuntimeError, ValueError) as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("中断しました。", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
