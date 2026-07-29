#!/usr/bin/env python3
"""无副作用探测 FlashAttentionScoreGrad 相关路径。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SOURCE_DIRS = [
    "attention/flash_attention_score_grad",
]

HARNESS_FILES = [
    "run_fag.py",
    "run_with_pta.sh",
    "run_with_tilingKey.sh",
    "fag_test/config.py",
    "fag_test/golden.py",
    "fag_test/pipeline.py",
    "fag_test/runner.py",
    "fag_test/test_utils.py",
    "fag_test/show_prof.py",
    "docs/debug_notes.md",
    "docs/pse_shapes.md",
]


def find_workspace_root(start: Path) -> Path:
    for path in [start, *start.parents]:
        if (path / "run_fag.py").exists() or any((path / p).exists() for p in SOURCE_DIRS):
            return path
    return start


def rel_status(root: Path, rel_paths: list[str]) -> list[dict[str, object]]:
    rows = []
    for rel in rel_paths:
        path = root / rel
        rows.append(
            {
                "path": rel,
                "exists": path.exists(),
                "type": "dir" if path.is_dir() else "file" if path.is_file() else "missing",
            }
        )
    return rows


def latest_files(root: Path, pattern: str, limit: int) -> list[dict[str, object]]:
    files = sorted(root.glob(pattern), key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    return [
        {"path": str(path.relative_to(root)), "bytes": path.stat().st_size}
        for path in files[:limit]
        if path.is_file()
    ]


def log_signals(root: Path, limit: int) -> list[str]:
    log = root / "run_log.txt"
    if not log.exists():
        return []
    try:
        lines = log.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    signals = [line for line in lines if any(token in line for token in ["error:", "Traceback", "diff_max", "dq", "dk", "dv"])]
    return signals[-limit:]


def main() -> int:
    parser = argparse.ArgumentParser(description="探测 FlashAttentionScoreGrad 工作区路径和近期产物。")
    parser.add_argument("--root", default=".", help="工作区根目录，或其下任意路径。")
    parser.add_argument("--json", action="store_true", help="输出 JSON，而不是普通文本。")
    parser.add_argument("--limit", type=int, default=5, help="展示的最新文件/日志信号数量。")
    args = parser.parse_args()

    root = find_workspace_root(Path(args.root).resolve())
    data = {
        "workspace_root": str(root),
        "source_trees": rel_status(root, SOURCE_DIRS),
        "harness_files": rel_status(root, HARNESS_FILES),
        "latest_results": latest_files(root, "results/FlashAttentionScoreGrad_Result_*", args.limit),
        "top_level_results": latest_files(root, "FlashAttentionScoreGrad_Result_*", args.limit),
        "recent_log_signals": log_signals(root, args.limit),
    }

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    print(f"工作区: {data['workspace_root']}")
    print("\n源码树:")
    for row in data["source_trees"]:
        marker = "OK" if row["exists"] else "--"
        print(f"  [{marker}] {row['path']}")
    print("\n调试工具文件:")
    for row in data["harness_files"]:
        marker = "OK" if row["exists"] else "--"
        print(f"  [{marker}] {row['path']}")
    print("\n最新结果:")
    for row in data["latest_results"] or data["top_level_results"]:
        print(f"  {row['path']} ({row['bytes']} bytes)")
    print("\n近期日志信号:")
    for line in data["recent_log_signals"]:
        print(f"  {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
