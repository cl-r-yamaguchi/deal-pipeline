"""Stop フック: Claude の応答が終わるたびに pytest を実行する。

- 全テストが通れば、何も出力せず静かに終わる
- 失敗したら、失敗内容を Claude に返して修正させる(decision: block)
- 差し戻しは 1 回で打ち切る(stop_hook_active が true のときは何もしない)
Windows と macOS のどちらでも動くよう、標準ライブラリだけで書いている。
"""
import json
import os
import subprocess
import sys

MAX_REASON_CHARS = 4000
NO_TESTS_COLLECTED = 5


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        event = {}
    # すでにフックの差し戻しで続行中なら、ループを防ぐために終了する
    if event.get("stop_hook_active"):
        return 0

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "--tb=short", "-p", "no:cacheprovider"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        print(json.dumps({"decision": "block", "reason": f"pytest を実行できませんでした: {e}"}, ensure_ascii=False))
        return 0

    if result.returncode in (0, NO_TESTS_COLLECTED):
        return 0

    output = (result.stdout + result.stderr).strip()
    if len(output) > MAX_REASON_CHARS:
        output = "...(前半省略)\n" + output[-MAX_REASON_CHARS:]
    reason = "pytest が失敗しました。内容を確認して修正してください。\n\n" + output
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
