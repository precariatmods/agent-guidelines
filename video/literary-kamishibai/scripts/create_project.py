#!/usr/bin/env python3
"""Create a literary-kamishibai project from the bundled template."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path


PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy basetemplate into scenario/projects and initialize its draft inputs."
    )
    parser.add_argument("--workspace-root", required=True, type=Path)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--source-file", type=Path)
    parser.add_argument("--brief-file", type=Path)
    parser.add_argument("--author")
    parser.add_argument("--author-death-year")
    parser.add_argument("--source-url")
    parser.add_argument("--publication-year")
    parser.add_argument("--publication-region")
    return parser.parse_args()


def require_file(path: Path | None, label: str) -> Path | None:
    if path is None:
        return None
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise SystemExit(f"{label} does not exist or is not a file: {resolved}")
    return resolved


def main() -> int:
    args = parse_args()
    if not PROJECT_ID_RE.fullmatch(args.project_id) or args.project_id == "basetemplate":
        raise SystemExit(
            "project-id must use letters, digits, underscore, or hyphen and cannot be basetemplate"
        )
    if not args.title.strip():
        raise SystemExit("title must not be empty")

    workspace = args.workspace_root.expanduser().resolve()
    projects_root = (workspace / "scenario" / "projects").resolve()
    destination = (projects_root / args.project_id).resolve()
    if destination.parent != projects_root:
        raise SystemExit("resolved destination escaped scenario/projects")
    if destination.exists():
        raise SystemExit(f"destination already exists; refusing to overwrite: {destination}")

    source_file = require_file(args.source_file, "source-file")
    brief_file = require_file(args.brief_file, "brief-file")
    template = Path(__file__).resolve().parent.parent / "assets" / "basetemplate"
    if not template.is_dir():
        raise SystemExit(f"bundled template is missing: {template}")

    projects_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template, destination)

    job_path = destination / "job.json"
    job = json.loads(job_path.read_text(encoding="utf-8-sig"))
    job["project_id"] = args.project_id
    job["title"] = args.title.strip()
    job_path.write_text(
        json.dumps(job, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    draft_source = destination / "sozai" / "source" / "original_source.txt"
    if source_file is not None:
        shutil.copyfile(source_file, draft_source)

    if brief_file is not None:
        shutil.copyfile(brief_file, destination / "sozai" / "idea.md")

    notes_path = destination / "sozai" / "source" / "source_notes.md"
    note_lines = [
        "# 新作案 原典メモ",
        "",
        f"- 作品名: {args.title.strip()}",
        f"- 原作者: {args.author or ''}",
        f"- 発表年: {args.publication_year or ''}",
        f"- 参照元: {args.source_url or ''}",
        "- 残したい文章:",
        "",
    ]
    notes_path.write_text("\n".join(note_lines), encoding="utf-8")

    rights_path = destination / "sozai" / "source" / "rights_check.md"
    rights_lines = [
        "# 権利確認案",
        "",
        f"- 原作者: {args.author or ''}",
        f"- 没年: {args.author_death_year or ''}",
        f"- 原典: {args.source_url or ''}",
        f"- 制作・公開地域での扱い: {args.publication_region or ''}",
        f"- 参照元: {args.source_url or ''}",
        "- 未確認事項:",
        "",
    ]
    rights_path.write_text("\n".join(rights_lines), encoding="utf-8")

    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
