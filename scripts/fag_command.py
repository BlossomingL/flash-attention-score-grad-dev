#!/usr/bin/env python3
"""生成 fag_debug_tools/run_fag.py 常用命令。"""

from __future__ import annotations

import argparse
import shlex


PRESETS = {
    "golden": ["--golden-only"],
    "accuracy": ["--pta", "--pta_mode=only_grad"],
    "profiler": ["--pta_mode=profiler"],
    "flash-golden": ["--golden-only", "--flash-golden"],
    "nosave-accuracy": ["--no-save-golden", "--flash-golden", "--pta_mode=only_grad"],
}


SCRIPT_PRESETS = {
    "pta-script": "bash ./run_with_pta.sh <CANN_PACKAGE_PATH>",
    "tilingkey-script": "bash ./run_with_tilingKey.sh <CANN_PACKAGE_PATH> <OPS_TRANSFORMER_ROOT> <FAG_TEST_ROOT>",
}


def choose_run_mode() -> str:
    print("请选择跑用例模式：")
    print("1. 无需编译直接跑")
    print("2. 先构建指定 tiling_key 再跑")
    while True:
        choice = input("请输入 1 或 2: ").strip()
        if choice == "1":
            return SCRIPT_PRESETS["pta-script"]
        if choice == "2":
            return SCRIPT_PRESETS["tilingkey-script"]
        print("输入无效，请重新选择。")


CASE_PRESETS = {
    "default": "./data/FASG.xls",
    "merged": "./data/FASG_merged.xls",
    "david": "./data/FASG_David.xls",
    "tnd": "./data/FASG_TND1.xls",
    "pse": "./data/FASG_PSE_cases.csv",
}


def quote_sh(arg: str) -> str:
    if not arg or any(ch.isspace() for ch in arg):
        return shlex.quote(arg)
    return arg


def main() -> int:
    parser = argparse.ArgumentParser(description="根据常用预设生成 run_fag.py 命令。")
    parser.add_argument("preset", choices=sorted([*PRESETS, *SCRIPT_PRESETS, "choose-run-mode"]), help="运行模式预设。")
    parser.add_argument("--case-preset", choices=sorted(CASE_PRESETS), default="default")
    parser.add_argument("--case", help="显式指定用例文件路径，会覆盖 --case-preset。")
    parser.add_argument("--sheet", default="Sheet1")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=2)
    parser.add_argument("--device", default="0")
    parser.add_argument("--python", default="python3")
    args = parser.parse_args()

    if args.preset == "choose-run-mode":
        print("cd <FAG_TEST_ROOT>")
        print(choose_run_mode())
        return 0

    if args.preset in SCRIPT_PRESETS:
        print("cd <FAG_TEST_ROOT>")
        print(SCRIPT_PRESETS[args.preset])
        return 0

    case = args.case or CASE_PRESETS[args.case_preset]
    command = [
        args.python,
        "-u",
        "./run_fag.py",
        "--case",
        case,
        "--sheet",
        args.sheet,
        "--device",
        str(args.device),
        "--start-from",
        str(args.start),
        "--end-at",
        str(args.end),
        *PRESETS[args.preset],
    ]
    print("cd <FAG_TEST_ROOT>")
    print(" ".join(quote_sh(part) for part in command))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
