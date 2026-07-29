#!/usr/bin/env python3
"""生成 FlashAttentionScoreGrad 测试计划 Markdown 骨架。"""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path


SECTIONS = {
    "precision": "精度测试",
    "performance": "性能测试",
    "board": "上板调试",
    "cpu-sim": "CPU 仿真",
}

DEFAULT_TEST_CODE = "https://gitcode.com/coder_linx/fag_debug_tools/"


def selected_sections(mode: str) -> list[str]:
    if mode == "all":
        return ["precision", "performance", "board", "cpu-sim"]
    return [mode]


def prompt_value(prompt: str, default: str | None = None, required: bool = False) -> str:
    suffix = f" [{default}]" if default else ""
    while True:
        value = input(f"{prompt}{suffix}: ").strip()
        if value:
            return value
        if default is not None:
            return default
        if not required:
            return ""
        print("该字段不能为空，请重新输入。")


def render_plan(topic: str, mode: str, cann_package: str, test_code: str) -> str:
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"# FlashAttentionScoreGrad 测试计划：{topic}",
        "",
        f"- 创建时间：{now}",
        f"- CANN 包路径：{cann_package or 'TODO'}",
        f"- 测试代码路径：{test_code or DEFAULT_TEST_CODE}",
        "- 目标源码树：TODO",
        "- 目标 commit：TODO",
        "- 执行环境：TODO",
        "- 结论：TODO",
        "",
        "## 用例范围",
        "",
        "| 类别 | case文件 | sheet | 行范围 | 说明 |",
        "| --- | --- | --- | --- | --- |",
        "| smoke | TODO | Sheet1 | TODO | TODO |",
        "| BNSD | TODO | Sheet1 | TODO | TODO |",
        "| TND | TODO | Sheet1 | TODO | TODO |",
        "| PSE | TODO | Sheet1 | TODO | TODO |",
        "",
    ]

    for key in selected_sections(mode):
        title = SECTIONS[key]
        lines.extend([f"## {title}", ""])
        if key == "precision":
            lines.extend(
                [
                    "- 目标：TODO",
                    f"- CANN 包路径：{cann_package or 'TODO'}",
                    f"- 测试代码路径：{test_code or DEFAULT_TEST_CODE}",
                    "- golden 命令：TODO",
                    "- NPU 精度命令：TODO",
                    "- 关注输出：dq / dk / dv / TODO",
                    "- 通过标准：TODO",
                    "- 结果表：TODO",
                    "- 失败归因：TODO",
                    "",
                ]
            )
        elif key == "performance":
            lines.extend(
                [
                    "- 目标：TODO",
                    f"- CANN 包路径：{cann_package or 'TODO'}",
                    f"- 测试代码路径：{test_code or DEFAULT_TEST_CODE}",
                    "- profiler 命令：TODO",
                    "- 基线文件：TODO",
                    "- 指标：Actual_kernel_time_backward / op_summary / TODO",
                    "- 回退阈值：TODO",
                    "- 结果表：TODO",
                    "- 瓶颈归因：TODO",
                    "",
                ]
            )
        elif key == "board":
            lines.extend(
                [
                    f"- CANN 包路径：{cann_package or 'TODO'}",
                    f"- 测试代码路径：{test_code or DEFAULT_TEST_CODE}",
                    "- 板端地址/别名：TODO",
                    "- SoC/device：TODO",
                    "- CANN/驱动/torch_npu：TODO",
                    "- 部署路径：TODO",
                    "- 环境初始化命令：TODO",
                    "- 精度复现命令：TODO",
                    "- 性能复现命令：TODO",
                    "- 回收产物：TODO",
                    "",
                ]
            )
        elif key == "cpu-sim":
            lines.extend(
                [
                    f"- CANN 包路径：{cann_package or 'TODO'}",
                    f"- 测试代码路径：{test_code or DEFAULT_TEST_CODE}",
                    "- 仿真工具链：TODO",
                    "- host tiling 构建命令：TODO",
                    "- host tiling 运行命令：TODO",
                    "- kernel 仿真构建命令：TODO",
                    "- kernel 仿真运行命令：TODO",
                    "- golden 对齐方式：TODO",
                    "- 仿真限制：TODO",
                    "",
                ]
            )

    lines.extend(
        [
            "## 产物清单",
            "",
            "| 产物 | 路径 | 说明 |",
            "| --- | --- | --- |",
            "| 结果表 | TODO | TODO |",
            "| run_log | TODO | TODO |",
            "| profiler | TODO | TODO |",
            "| CPU仿真输出 | TODO | TODO |",
            "",
            "## 结论与下一步",
            "",
            "- 结论：TODO",
            "- 风险：TODO",
            "- 下一步：TODO",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="生成 FAG 精度/性能/上板/CPU 仿真测试计划骨架。")
    parser.add_argument("--topic", default="未命名测试", help="测试主题。")
    parser.add_argument("--mode", choices=["all", *SECTIONS.keys()], default="all", help="计划类型。")
    parser.add_argument("--cann-package", default="", help="CANN 包路径。")
    parser.add_argument(
        "--test-code",
        nargs="?",
        const=DEFAULT_TEST_CODE,
        default=DEFAULT_TEST_CODE,
        help=f"测试代码路径；不传或不填写参数时使用默认值 {DEFAULT_TEST_CODE}",
    )
    parser.add_argument("--interactive", action="store_true", help="交互确认 CANN 包路径和测试代码路径。")
    parser.add_argument("--output", help="输出文件路径；不传则打印到 stdout。")
    args = parser.parse_args()

    cann_package = args.cann_package
    test_code = args.test_code or DEFAULT_TEST_CODE
    if args.interactive:
        cann_package = prompt_value("请输入 CANN 包路径", required=True)
        test_code = prompt_value("请输入测试代码路径，留空使用默认值", default=DEFAULT_TEST_CODE)

    content = render_plan(args.topic, args.mode, cann_package, test_code)
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"已生成: {path}")
    else:
        print(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
