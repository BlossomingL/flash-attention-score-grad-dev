# 精度定位流程

当用户报告 dq/dk/dv 不一致、`diff_max`、结果表失败、golden 问题，或怀疑 PSE/mask/dropout/rope/TND 场景异常时，读取本文件。

如果用户要先生成用例表，或指定 case 表和 sheet 跑用例，先读取 `case-running.md`。

## 分流流程

1. 用 `--start-from X --end-at X+1` 单行复现。
2. 先跑 `--golden-only`，验证用例解析和 golden 生成。
3. 再优先参考 `<FAG_TEST_ROOT>/run_with_pta.sh` 的 PTA 调测链路跑 NPU 精度。
4. 如果失败，仅在确认 golden 产物与当前代码匹配时，才使用 `--cache-data` 复跑。
5. 改代码前先归类：环境/依赖问题、非法用例、能力限制、golden/脚本问题、疑似算子精度问题。

## 日常 PTA 脚本

精度验证优先参考：

```bash
cd <FAG_TEST_ROOT>
bash ./run_with_pta.sh <CANN_PACKAGE_PATH>
```

该脚本的核心动作：

- 打印 CANN 包路径并设置 `CANN_PATH=$1`。
- `source <CANN_PACKAGE_PATH>/cann/bin/setenv.bash`。
- 执行 `asys info -r=status` 检查环境。
- 通过 `msprof --output=./profiling` 运行 `python3 run_fag.py --case ./data/FASG.xls --pta --pta-mode only_grad --sheet sheet1 --no-save-golden`。
- 执行 `python3 show_prof.py` 查看 profiling 结果。

## 常用命令

在 `<FAG_TEST_ROOT>` 下执行；这些命令用于 golden-only、单行复现或临时改参数，正式 PTA 调测优先对齐 `run_with_pta.sh`：

```powershell
python -u .\run_fag.py --golden-only --case .\data\FASG.xls --sheet Sheet1 --start-from 1 --end-at 2
python -u .\run_fag.py --case .\data\FASG.xls --sheet Sheet1 --pta --pta_mode=only_grad --device 0 --start-from 1 --end-at 2
python -u .\run_fag.py --case .\data\FASG.xls --sheet Sheet1 --cache-data --pta_mode=only_grad --device 0 --start-from 1 --end-at 2
```

大 shape 或内存压力场景：

```powershell
python -u .\run_fag.py --golden-only --flash-golden --case .\data\FASG.xls --sheet Sheet1 --start-from 1 --end-at 2
python -u .\run_fag.py --case .\data\FASG.xls --sheet Sheet1 --no-save-golden --flash-golden --pta_mode=only_grad --device 0 --start-from 1 --end-at 2
```

批量预设：

```powershell
python -u .\run_fag.py --case .\data\FASG_David.xls --sheet Sheet1 --pta --pta_mode=only_grad --device 0 --start-from 1 --end-at -1
python -u .\run_fag.py --case .\data\FASG_TND1.xls --sheet Sheet1 --pta --pta_mode=only_grad --device 0 --start-from 1 --end-at -1
python -u .\run_fag.py --case .\data\FASG_PSE_cases.csv --sheet Sheet1 --pta --pta_mode=only_grad --device 0 --start-from 1 --end-at -1
```

## 证据检查

最新结果表：

```powershell
Get-ChildItem .\results\FlashAttentionScoreGrad_Result_* | Sort-Object LastWriteTime -Descending | Select-Object -First 5
```

日志信号：

```powershell
Get-Content .\run_log.txt -Tail 200
Select-String -Path .\run_log.txt -Pattern "error:","Traceback","diff_max","dq","dk","dv"
```

结果表中优先检查：

- `Actual_dq_pricision`
- `Actual_dk_pricision`
- `Actual_dv_pricision`
- `Actual_kernel_time_backward`
- deterministic 输出：`Actual_dq_Md5sum`、`Actual_dk_Md5sum`、`Actual_dv_Md5sum`

## 通过/失败判定

主判定来自 `fag_test/test_utils.py::check_result`。

优先级：

1. Traceback、tiling 失败、shape 不一致或运行时错误。
2. `check_result` 中的 `error:` 和 `diff_max`。
3. `diff_sum` 和错误率。
4. `print_compare` 误差分布只作为辅助证据。

在确认 golden 生成、用例合法性和能力限制之前，不要直接把问题归为算子精度 bug。

## 常见分支

Golden 生成失败：

- 检查 `input_layout`、`N1/N2` 分组、`D/D_V`、`rope`、`pse_type`、`pse_shape`、TND 序列元数据。
- PSE 问题读取 `fag_debug_tools/docs/pse_shapes.md`。
- 历史限制读取 `fag_debug_tools/docs/debug_notes.md`。

NPU tiling 或执行失败：

- 记录 case 名称、dtype/out_dtype、B/N1/N2/S1/S2/D/D_V、layout、sparse_mode、mask/PSE、pre_tockens/next_tockens、dropout、rope、sink、deterministic、完整 error code。
- 非法 PSE 组合和已知能力缺口要与精度失败分开处理。

精度不一致：

- 复跑同一行。
- 在有效前提下复用稳定 golden。
- dropout 场景核对 seed/offset 和 Philox 路径。
- mask/PSE 场景核对 NPU 侧 `pse` 与 golden 侧 `pse_golden` 语义。
- rope 场景核对 `dq/dk` 与 `dq_rope/dk_rope` 切分。
- TND 场景核对 unpad、`cu_seqlens_q`、`cu_seqlens_kv`、每段实际长度。
- 只有单个输出失败时先追该输出路径；三个输出都失败时，优先查 softmax/dsink/mask/PSE/dropout 共享路径。

## 报告模板

```markdown
## 测试结论

- 结论: 通过 / 失败 / 部分通过 / 未完成
- 环境: device=<id>, pta_mode=<mode>, NPU是否实际运行
- 命令: `python -u run_fag.py ...`
- 用例: <case file> / <sheet> / rows <start>-<end>
- 结果: `results/FlashAttentionScoreGrad_Result_<timestamp>.*`
- 日志: `run_log.txt`

## 精度摘要

| Case | dq | dk | dv | diff_max摘要 | 结论 |
| --- | --- | --- | --- | --- | --- |

## 归因

| Case | 现象 | 初步归因 | 下一步 |
| --- | --- | --- | --- |
```
