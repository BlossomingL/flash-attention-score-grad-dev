# 测试框架

当需要搭建或扩展 FlashAttentionScoreGrad 的精度测试、性能测试、上板调试、CPU 仿真流程时，读取本文件。本文件只给框架和接口位，具体平台命令、环境变量、CI 名称、板卡地址、仿真器路径由维护者补充。

## 执行前确认

在生成测试计划、上板部署、CPU 仿真或实际执行精度/性能测试前，先提示使用者确认：

- CANN 包路径：必须由使用者输入，用于构建、部署或板端环境初始化。
- 测试代码路径：提示使用者输入；如果留空，使用默认测试代码 `https://gitcode.com/coder_linx/fag_debug_tools/`。

如果用户只是在编辑文档或补 TODO，可以不要求这两个输入；一旦进入“生成可执行计划/命令/部署动作”，必须记录这两个字段。

交互生成计划：

```powershell
python .\flash-attention-score-grad-dev\scripts\fag_test_plan.py --topic "pse精度回归" --mode all --interactive
```

非交互生成计划：

```powershell
python .\flash-attention-score-grad-dev\scripts\fag_test_plan.py --topic "pse精度回归" --mode all --cann-package "TODO" --test-code "https://gitcode.com/coder_linx/fag_debug_tools/"
```

## 流程总览

把测试分成四条可独立组合的链路：

- 精度测试：确认 CANN 包和测试代码 -> 用例解析 -> 输入/golden 生成 -> 算子执行 -> dq/dk/dv 比对 -> 失败归因。
- 性能测试：用例选择 -> profiler/计时执行 -> op_summary/result 表解析 -> 基线对比 -> 瓶颈归因。
- 上板调试：确认 CANN 包和测试代码 -> 构建产物 -> 部署到板端 -> 设置运行环境 -> 单 case 复现 -> 日志/产物回收。
- CPU 仿真：确认 CANN 包和测试代码 -> 构建 host/仿真目标 -> 执行 tiling 或 kernel 仿真 -> 对照 golden -> 输出可复现报告。

默认顺序：

1. 先在本地跑 `--golden-only` 或 CPU 仿真，排除用例和 golden 问题。
2. 再上板跑单行精度 smoke。
3. 精度稳定后跑性能 smoke。
4. 最后按类别扩展到 BNSD、TND、PSE、dropout、rope、sink、deterministic。

## 目录建议

在实际项目中可以按以下结构沉淀测试资产，具体位置由维护者决定：

```text
<workspace>/
  fag_debug_tools/
    data/                         # 用例表
    auto_input/                   # 输入/golden 产物
    results/                      # 精度/性能结果表
    run_log.txt                   # 工具日志
  test_runs/
    <YYYYMMDD_HHMMSS>_<topic>/
      plan.md                     # 本次测试计划
      commands.ps1                # 实际执行命令
      board/                      # 上板日志和回收产物
      cpu_sim/                    # CPU 仿真日志和产物
      results/                    # 结果表副本
      summary.md                  # 结论
```

可以用以下脚本生成 `plan.md` 骨架：

```powershell
python .\flash-attention-score-grad-dev\scripts\fag_test_plan.py --topic "pse精度回归" --mode all --interactive
```

## 精度测试框架

目标：

- 覆盖 `dq`、`dk`、`dv`，以及按需覆盖 `dq_rope`、`dk_rope`、`dsink`。
- 区分脚本/golden 问题、用例非法、能力限制、NPU 执行失败、真实精度偏差。
- 对每个失败 case 保存可复现命令和最小证据。

分层：

- L0 smoke：每类 1 到 2 行，验证工具链、golden、NPU 调用通路。
- L1 feature：按 BNSD/TND/PSE/dropout/rope/sink/deterministic 分类覆盖。
- L2 regression：按目标表全量或分段跑，输出失败汇总。
- L3 stress：大 S、大 D、特殊 sparse_mode、边界 keep_prob、极端 mask/PSE。

待维护者补充：

- TODO：每层对应的用例表和行范围。
- TODO：各 dtype/out_dtype 的覆盖要求。
- TODO：特殊场景的预期能力限制清单。
- TODO：精度阈值、豁免规则和报告字段。

推荐命令入口：

```powershell
Set-Location .\fag_debug_tools
python -u .\run_fag.py --golden-only --case .\data\FASG.xls --sheet Sheet1 --start-from 1 --end-at 2
python -u .\run_fag.py --case .\data\FASG.xls --sheet Sheet1 --pta --pta_mode=only_grad --device 0 --start-from 1 --end-at 2
```

失败定位细节读取 `precision-debug.md`。

## 性能测试框架

目标：

- 记录 `Actual_kernel_time_backward` 和 profiler/op_summary 证据。
- 保持同 shape、同输入、同环境、同构建对比。
- 输出基线、当前值、变化比例、疑似瓶颈、下一步实验。

分层：

- P0 smoke：单行 profiler，确认 profiler 可用和结果表可写。
- P1 representative：按 BNSD/TND/PSE/大 S/小 D 等代表 shape 收集。
- P2 regression：与固定基线表比对，筛出超过阈值的 case。
- P3 deep dive：对慢 case 关联 tiling key、cube/vector 路径、buffer 使用和 op_summary。

待维护者补充：

- TODO：性能基线文件位置和格式。
- TODO：性能波动阈值，如 `+5%`、`+10us` 等。
- TODO：profiler 产物目录和 `show_prof.py` 固定用法。
- TODO：不同板卡/SoC 的分组规则。

推荐命令入口：

```powershell
Set-Location .\fag_debug_tools
python -u .\run_fag.py --case .\data\FASG.xls --sheet Sheet1 --pta_mode=profiler --device 0 --start-from 1 --end-at 2
```

瓶颈分析细节读取 `performance-analysis.md`。

## 上板调试框架

目标：

- 在真实 NPU/Ascend 板端复现精度或性能问题。
- 固定构建版本、运行环境、输入/golden、日志和 profiler 产物。
- 保证本地结论能追溯到具体 commit、板卡、CANN/驱动/torch_npu 版本。

阶段：

1. 构建准备：确认目标源码树、commit、编译选项、SoC、debug 开关。
2. 产物部署：上传算子包、Python 工具、用例表、必要输入/golden。
3. 环境设置：加载 CANN、Python、torch_npu、device、日志级别、profiling 开关。
4. 单 case 复现：先跑最小行范围，保存命令、stdout、`run_log.txt`。
5. 产物回收：回收结果表、profiler、dump、kernel 日志、md5 或二进制输出。
6. 归档报告：记录环境、命令、结果、初步归因和下一步。

待维护者补充：

- TODO：板端登录方式和工作目录。
- TODO：源码/算子包构建命令。
- TODO：部署脚本或 scp/rsync 规范。
- TODO：板端环境变量模板。
- TODO：日志和 profiler 产物回收路径。
- TODO：debug dump 开关和清理规则。

上板命令模板：

```powershell
# TODO: 填写板端连接方式
# ssh <board>

# TODO: 填写板端环境初始化
# source <cann_env>
# export ASCEND_VISIBLE_DEVICES=0

Set-Location .\fag_debug_tools
python -u .\run_fag.py --case .\data\FASG.xls --sheet Sheet1 --pta --pta_mode=only_grad --device 0 --start-from 1 --end-at 2
python -u .\run_fag.py --case .\data\FASG.xls --sheet Sheet1 --pta_mode=profiler --device 0 --start-from 1 --end-at 2
```

## CPU 仿真框架

目标：

- 在无板卡或上板前，通过 host/CPU 仿真先验证 tiling、shape、参数合法性和部分 kernel 逻辑。
- 让算子问题尽量在本地复现，减少上板迭代成本。
- 明确 CPU 仿真能验证什么、不能验证什么。

推荐分层：

- C0 golden-only：只跑 `fag_debug_tools --golden-only`，验证 Excel/CSV、输入生成、golden 数学。
- C1 host tiling：执行 op_host/tiling 单测或仿真入口，验证 tiling key、tiling data、shape/infer。
- C2 kernel sim：执行 CPU/AscendC 仿真器入口，验证 kernel 主要分支和输出。
- C3 compare：用同一输入比较仿真输出与 golden，产出 dq/dk/dv 差异摘要。

待维护者补充：

- TODO：CPU 仿真工具链名称、安装位置和版本要求。
- TODO：host tiling 单测构建和运行命令。
- TODO：kernel 仿真入口、参数文件和输出目录。
- TODO：仿真输出与 `fag_debug_tools` golden 的对齐格式。
- TODO：仿真不覆盖的 NPU 行为清单。

CPU 仿真命令模板：

```powershell
Set-Location .\fag_debug_tools
python -u .\run_fag.py --golden-only --case .\data\FASG.xls --sheet Sheet1 --start-from 1 --end-at 2

# TODO: 填写 host tiling 构建命令
# TODO: 填写 host tiling 运行命令

# TODO: 填写 kernel CPU 仿真构建命令
# TODO: 填写 kernel CPU 仿真运行命令

# TODO: 填写仿真输出与 golden 比对命令
```

## 结果归档模板

每次正式测试至少记录：

- 测试主题、目标源码树、commit、执行人、时间。
- 环境：本地/板端/CPU 仿真、SoC、device、CANN 包路径、torch_npu、Python。
- 测试代码：使用者输入路径；留空时记录默认测试代码 `https://gitcode.com/coder_linx/fag_debug_tools/`。
- 用例：case 文件、sheet、行范围、关键 shape 分类。
- 命令：golden、上板精度、上板性能、CPU 仿真。
- 产物：结果表、日志、profiler、dump、仿真输出。
- 结论：通过/失败/部分通过/未完成。
- 归因：用例问题、golden 问题、能力限制、算子问题、环境问题、待确认。

## 自动化接口占位

后续可以补充以下自动化，但现在只保留接口：

- TODO：从结果表自动提取失败 case。
- TODO：从 result 表生成性能回退报告。
- TODO：按 case 分类生成分段运行命令。
- TODO：自动收集板端日志和 profiler 产物。
- TODO：自动生成 CPU 仿真参数文件。
