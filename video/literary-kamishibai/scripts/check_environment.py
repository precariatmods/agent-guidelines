from __future__ import annotations

import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
VOICEVOX_VERSION_URL = "http://127.0.0.1:50021/version"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def command_version(command: str, args: list[str]) -> tuple[bool, str]:
    executable = shutil.which(command)
    if executable is None:
        return False, "見つかりません"
    import subprocess

    result = subprocess.run(
        [executable, *args], capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    output = (result.stdout or result.stderr).strip().splitlines()
    return result.returncode == 0, output[0] if output else executable


def main() -> int:
    checks: list[tuple[str, bool, str]] = []
    checks.append(("Python", sys.version_info >= (3, 10), sys.version.split()[0]))
    node_ok, node_version = command_version("node", ["--version"])
    npm_ok, npm_version = command_version("npm", ["--version"])
    checks.append(("Node.js", node_ok, node_version))
    checks.append(("npm", npm_ok, npm_version))

    remotion_dir = ROOT / "remotion"
    remotion_installed = (remotion_dir / "node_modules" / "@remotion" / "cli").exists()
    install_command = "npm ci" if (remotion_dir / "package-lock.json").exists() else "npm install"
    checks.append(
        (
            "Remotion",
            remotion_installed,
            (
                "導入済み（再インストール不要）"
                if remotion_installed
                else (
                    "未導入（初回だけ導入してください）\n"
                    f'    cd "{remotion_dir}"\n'
                    f"    {install_command}"
                )
            ),
        )
    )

    try:
        with urllib.request.urlopen(VOICEVOX_VERSION_URL, timeout=2) as response:
            voicevox_version = response.read().decode("utf-8").strip().strip('"')
        voicevox_ok = True
    except (urllib.error.URLError, TimeoutError, OSError):
        voicevox_ok = False
        voicevox_version = "接続できません: VOICEVOX Engineを起動してください"
    checks.append(("VOICEVOX Engine", voicevox_ok, voicevox_version))

    for name, ok, detail in checks:
        print(f"[{'OK' if ok else 'NG'}] {name}: {detail}")

    return 0 if all(ok for _, ok, _ in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
