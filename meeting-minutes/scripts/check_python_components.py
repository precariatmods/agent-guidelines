"""Check that the packages in requirements.txt are installed and importable."""

from __future__ import annotations

import argparse
import importlib.metadata
import sys
from pathlib import Path


def read_requirements(path: Path) -> list[tuple[str, str]]:
    requirements: list[tuple[str, str]] = []
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        name, separator, version = line.partition("==")
        if not separator or not name.strip() or not version.strip():
            raise RuntimeError(f"固定バージョンではない依存関係があります: {line}")
        requirements.append((name.strip(), version.strip()))
    return requirements


def ensure_components(requirements_path: Path) -> None:
    requirements_path = requirements_path.resolve()
    requirements = read_requirements(requirements_path)
    problems: list[str] = []
    for package, expected in requirements:
        try:
            installed = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            problems.append(f"{package}=={expected} が未導入です")
            continue
        if installed != expected:
            problems.append(
                f"{package} のバージョンが異なります: "
                f"導入済み={installed}, 必要={expected}"
            )
            continue
    if problems:
        command = f'"{sys.executable}" -m pip install -r "{requirements_path}"'
        raise RuntimeError("\n".join(problems) + f"\n導入コマンド:\n{command}")


def main() -> int:
    parser = argparse.ArgumentParser(description="必要なPythonパッケージを確認します。")
    parser.add_argument(
        "--requirements",
        type=Path,
        default=Path(__file__).with_name("requirements.txt"),
    )
    args = parser.parse_args()
    try:
        ensure_components(args.requirements)
    except (OSError, RuntimeError) as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        return 2
    print("Pythonパッケージ確認: 正常", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
