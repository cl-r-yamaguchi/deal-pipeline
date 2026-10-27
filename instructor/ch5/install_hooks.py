"""Hooks を .claude/ に入れる(講師用)。

- .claude/hooks/run_tests.py をコピーする
- .claude/settings.json に Stop フックを追加する(既存の permissions などは残す)
使い方: プロジェクトのルートで  python instructor/ch5/install_hooks.py
何度実行しても、Stop フックは 1 つだけになる。
"""
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CLAUDE_DIR = ROOT / ".claude"


def main():
    hooks_dir = CLAUDE_DIR / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(HERE / "hooks" / "run_tests.py", hooks_dir / "run_tests.py")

    settings_path = CLAUDE_DIR / "settings.json"
    settings = {}
    if settings_path.exists():
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    hooks = json.loads((HERE / "settings.hooks.json").read_text(encoding="utf-8"))
    settings["hooks"] = {**settings.get("hooks", {}), **hooks["hooks"]}
    settings_path.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print("Hooks を入れました: .claude/hooks/run_tests.py と .claude/settings.json")


if __name__ == "__main__":
    main()
