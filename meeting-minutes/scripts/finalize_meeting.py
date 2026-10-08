"""Validate the four final CSV files and copy meeting.xlsx unchanged."""

from __future__ import annotations

import argparse
import csv
import shutil
import sys
from pathlib import Path


REQUIRED_CSV_NAMES = ("header.csv", "minutes.csv", "participants.csv", "Agenda.csv")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "outputの4種類のCSVを検証し、template/meeting.xlsxを"
            "内容を変更せずoutput/meeting.xlsxへコピーします。"
        )
    )
    parser.add_argument("output_dir", type=Path, help="4 CSVがある出力フォルダ")
    parser.add_argument(
        "--template",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "template" / "meeting.xlsx",
        help="そのままコピーするExcelテンプレート",
    )
    parser.add_argument("--force", action="store_true", help="既存のコピー先Excelを上書きする")
    return parser.parse_args()


def validate_csv(path: Path, expected_header: list[str]) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        header = next(reader, None)
        if header != expected_header:
            raise ValueError(
                f"{path.name}の列名・列順がテンプレートと一致しません: {header}"
            )
        rows = list(reader)
        populated = sum(
            1 for row in rows if any(str(cell).strip() for cell in row)
        )
        if populated == 0:
            raise ValueError(f"{path.name}にデータ行がありません。")
        return populated


def read_template_header(path: Path) -> list[str]:
    if not path.is_file():
        raise ValueError(f"CSVテンプレートが見つかりません: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        header = next(csv.reader(stream), None)
    if not header:
        raise ValueError(f"CSVテンプレートに列名がありません: {path}")
    return header


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    template = args.template.resolve()
    target = output_dir / "meeting.xlsx"

    try:
        if not template.is_file():
            raise ValueError(f"Excelテンプレートが見つかりません: {template}")
        if not output_dir.is_dir():
            raise ValueError(f"出力フォルダが見つかりません: {output_dir}")
        if target.exists() and not args.force:
            raise FileExistsError(
                f"コピー先Excelは既に存在します: {target}\n"
                "上書きする場合は--forceを指定してください。"
            )

        counts = {}
        template_dir = template.parent
        for name in REQUIRED_CSV_NAMES:
            csv_path = output_dir / name
            if not csv_path.is_file():
                raise ValueError(f"必要なCSVが見つかりません: {csv_path}")
            expected_header = read_template_header(template_dir / name)
            counts[name] = validate_csv(csv_path, expected_header)

        shutil.copy2(template, target)
        print(f"Excelコピー: {target}")
        for name, count in counts.items():
            print(f"{name}: {count}件")
    except (FileExistsError, OSError, ValueError) as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
