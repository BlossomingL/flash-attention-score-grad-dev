---
name: flash-attention-score-grad-dev
description: 支持用户指定路径下 FlashAttentionScoreGrad/FAG Ascend 算子的日常开发，包括源码导航、tiling/kernel 修改、调试运行、golden 生成、精度问题定位、结果/日志解读和性能分析。用于处理 FlashAttentionScoreGrad、flash_attention_score_grad、FAG 用例、dq/dk/dv 精度异常、TND/BNSD/PSE/dropout/rope/sink 场景，以及用户指定 ops-transformer 仓和测试脚本仓中的 profiler 分析任务。使用本 skill 时，无论用户提出什么需求，都必须先要求用户提供 ops-transformer 仓路径、测试脚本仓路径和 CANN 包路径。
---

# FlashAttentionScoreGrad 开发

## 强制前置确认

无论用户提出什么需求，先要求用户提供以下三项信息：

- `ops-transformer仓路径`：待开发或分析的算子源码仓路径。
- `测试脚本仓路径`：包含 `run_fag.py` 或等价 FAG 测试入口的测试代码路径。
- `CANN包路径`：用于构建、上板、仿真或环境确认的 CANN 安装包/工具包路径。

只有在用户已经明确给出这三项信息后，才能继续源码搜索、测试命令生成、精度定位、性能分析、上板调试、CPU 仿真或文档补充。不要用自动探测结果替代用户确认；探测结果只能在用户给出路径后用于校验。

用户输入的三项路径作为本轮和后续步骤的全局路径使用：

- 将 `ops-transformer仓路径` 记为 `<OPS_TRANSFORMER_ROOT>`，后续所有算子源码搜索、编辑、构建和 git 操作都基于它。
- 将 `测试脚本仓路径` 记为 `<FAG_TEST_ROOT>`，后续所有 `run_fag.py`、用例表、golden、结果表和日志操作都基于它。
- 将 `CANN包路径` 记为 `<CANN_PACKAGE_PATH>`，后续所有环境初始化、构建、上板和仿真说明都引用它。

不要在后续流程中重新猜测或切换这些路径；除非用户明确更新某个路径，否则一直沿用已确认的全局路径。

缺少任意一项时，先只追问缺失项：

```text
请先提供以下路径后我再继续：
- ops-transformer仓路径：
- 测试脚本仓路径：
- CANN包路径：
```

## 先看这里

把这个 skill 当作 FlashAttentionScoreGrad 开发手册。先判断用户目标属于源码开发、精度定位、性能分析还是测试工具维护，再只加载匹配的参考文档：

- 源码导航或实现修改：读取 `references/repo-map.md` 和 `references/development.md`。
- 跑用例、根据描述生成用例表、指定表格和 sheet：读取 `references/case-running.md`。
- 精度失败、dq/dk/dv 不一致、golden 问题、用例分流：读取 `references/precision-debug.md`。
- profiler、kernel time、慢用例、op_summary 分析：读取 `references/performance-analysis.md`。
- 不确定路径或最新产物：运行 `python flash-attention-score-grad-dev/scripts/fag_probe.py`。

默认不要直接跑全量用例。先跑单行或小范围 smoke，再决定是否扩大回归。

跑用例支持两种入口：

- 描述生成：用户手动输入用例描述，先读取 `<FAG_TEST_ROOT>/data` 下已有表格模板，再按模板字段生成新用例表。
- 指定表格：用户直接提供 case 表路径和 sheet，按用户指定表格运行，不自动改表。

正式跑用例前必须让用户选择运行模式：

- 无需编译直接跑：调用 `<FAG_TEST_ROOT>/run_with_pta.sh <CANN_PACKAGE_PATH>`。
- 先构建指定 tiling_key 再跑：调用 `<FAG_TEST_ROOT>/run_with_tilingKey.sh <CANN_PACKAGE_PATH> <OPS_TRANSFORMER_ROOT> <FAG_TEST_ROOT>`。

如果当前交互界面支持选择框，用选择框展示以上两个选项；如果不支持，直接用文字询问用户选择哪一种。

## 工作区默认入口

日常使用 `<FAG_TEST_ROOT>` 作为 Python 调试工具路径：

```bash
cd <FAG_TEST_ROOT>
python3 -u ./run_fag.py --golden-only --case ./data/FASG.xls --sheet Sheet1 --start-from 1 --end-at 2
python3 -u ./run_fag.py --case ./data/FASG.xls --sheet Sheet1 --pta --pta_mode=only_grad --device 0 --start-from 1 --end-at 2
python3 -u ./run_fag.py --case ./data/FASG.xls --sheet Sheet1 --pta_mode=profiler --device 0 --start-from 1 --end-at 2
```

常用文件：

- `fag_debug_tools/run_fag.py`：命令行入口。
- `fag_debug_tools/fag_test/config.py`：`soc_version`、`gtype`、调试开关、`CaseConfig`、`RuntimeContext`。
- `fag_debug_tools/fag_test/golden.py`：数学 golden，包含普通 golden 和 flash golden。
- `fag_debug_tools/fag_test/pipeline.py`：BNSD/TND 输入和 golden 生成流水线。
- `fag_debug_tools/fag_test/runner.py`：torch_npu 执行、结果比较、结果写回。
- `fag_debug_tools/fag_test/test_utils.py`：Excel/CSV 解析、日志、`check_result`、`print_compare`。
- `fag_debug_tools/fag_test/show_prof.py`：profiler CSV 展示。

## 操作规则

修改代码前先确认目标源码树。默认只使用用户输入的 `<OPS_TRANSFORMER_ROOT>`，不要切换到其他路径。

修改 golden 或测试工具逻辑时，先对受影响的最小用例跑 `--golden-only`。如果有 NPU 环境，再用同一用例跑 `--pta_mode=only_grad`。如果改动影响共享逻辑，再补一个相邻正常用例。

修改 tiling 或 kernel 代码时，记录路径选择条件：layout、dtype/out_dtype、B/N1/N2/S1/S2/D/D_V、sparse_mode、mask/PSE、dropout、rope、sink、deterministic、TND cu_seqlens。

解释结果时，优先依据 `check_result` 和 `diff_max`，不要只看 `print_compare` 的错误元素数。`print_compare` 是误差分布证据，不是最终通过/失败判定。

如果当前执行环境没有 NPU 或 `torch_npu`，只能声明完成了 golden/脚本级验证，并给出需要在 NPU 环境执行的精确命令。

## 可用脚本

- `scripts/fag_probe.py`：打印已发现的源码树、调试工具文件、最新结果和近期日志信号。
- `scripts/fag_command.py`：生成 golden-only、精度、profiler、batch、TND、PSE 等常用命令模板。

除非脚本另有说明，默认从包含本 skill 的目录运行；实际源码和测试操作仍以用户输入的全局路径为准。

## 日常验证脚本

所有精度和性能验证优先参考用户测试脚本仓中的两个日常调测脚本：

- `<FAG_TEST_ROOT>/run_with_pta.sh`：基于 `<CANN_PACKAGE_PATH>` 初始化 CANN 环境，检查 `asys` 状态，通过 `msprof` 执行 `run_fag.py`，最后调用 `show_prof.py`。
- `<FAG_TEST_ROOT>/run_with_tilingKey.sh`：基于 `<CANN_PACKAGE_PATH>`、`<OPS_TRANSFORMER_ROOT>`、`<FAG_TEST_ROOT>`，先构建并安装指定 tiling_key 的 `flash_attention_score_grad` 自定义算子包，再执行 `msprof + run_fag.py + show_prof.py`。

需要生成命令模板时，优先使用：

```bash
python3 ./scripts/fag_command.py choose-run-mode
python3 ./scripts/fag_command.py pta-script
python3 ./scripts/fag_command.py tilingkey-script
```
