# 性能分析流程

当用户询问 kernel time、profiler 模式、op_summary、慢用例、性能回退对比、cube/vector 瓶颈或性能优化时，读取本文件。

## 运行 profiler 模式

在 `fag_debug_tools` 下执行：

```powershell
python -u .\run_fag.py --case .\data\FASG.xls --sheet Sheet1 --pta_mode=profiler --device 0 --start-from 1 --end-at 2
```

按类别运行：

```powershell
python -u .\run_fag.py --case .\data\FASG_David.xls --sheet Sheet1 --pta_mode=profiler --device 0 --start-from 1 --end-at -1
python -u .\run_fag.py --case .\data\FASG_TND1.xls --sheet Sheet1 --pta_mode=profiler --device 0 --start-from 1 --end-at -1
python -u .\run_fag.py --case .\data\FASG_PSE_cases.csv --sheet Sheet1 --pta_mode=profiler --device 0 --start-from 1 --end-at -1
```

先跑小行范围。全量性能 sweep 可能耗时较长，应明确目标后再跑。

## 检查产物

主要证据：

- `results/FlashAttentionScoreGrad_Result_<timestamp>.*`
- 结果表中的 `Actual_kernel_time_backward`
- `run_log.txt`
- runtime 生成的 profiler `op_summary` CSV
- `fag_test/show_prof.py` 的展示结果

快速检查：

```powershell
Get-ChildItem .\results\FlashAttentionScoreGrad_Result_* | Sort-Object LastWriteTime -Descending | Select-Object -First 5
Get-Content .\run_log.txt -Tail 200
python .\fag_test\show_prof.py --help
```

依赖 `show_prof.py` 的参数前，先阅读当前脚本，保证命令示例与实际 CLI 一致。

## 分析清单

性能数据必须和用例 shape 绑定：

- B/N1/N2/S1/S2/D/D_V。
- layout：BNSD 类、SBH/BSH/BSND 或 TND。
- dtype 和 out_dtype。
- sparse_mode 与 band window。
- PSE/mask/dropout/rope/sink/deterministic 开关。
- 已知时记录选中的架构和 tiling 分支。

只比较同条件数据：

- 相同源码树和构建。
- 相同 CANN/torch_npu 环境。
- 相同 device。
- 测量算子改动时使用相同输入/golden。
- 相同 profiler warmup 假设。

## 瓶颈定位源码区域

tiling/key 选择：

- `op_host/flash_attention_score_grad_tiling.cpp`
- `op_host/arch35/flash_attention_score_grad_tiling_common_regbase.*`
- `op_host/arch35/flash_attention_score_grad_tiling_normal_regbase.*`
- `op_host/arch35/flash_attention_score_grad_tiling_varlen_regbase.cpp`
- `op_kernel/arch35/flash_attention_score_grad_template_tiling_key.h`

计算路径：

- `op_kernel/arch35/flash_attention_score_grad_kernel*.h`
- `op_kernel/arch35/flash_attention_score_grad_block_cube.h`
- `op_kernel/arch35/flash_attention_score_grad_block_vec.h`
- `op_kernel/arch35/vector_api/*.h`
- `op_kernel/arch35/cube_api/*.h`

内存和 buffer 行为：

- `op_kernel/arch35/flash_attention_score_grad_common.h`
- 活跃源码树中的 buffer 相关公共头文件。
- 顶层笔记：`buffer_allocation_analysis.md`、`cube_scalar_optimization_plan.md`。

## 输出报告

说明数字来源：profiler 模式、结果表 kernel time，还是日志推断。包含精确命令和结果产物。如果本地不能运行，给出应在 NPU 环境执行的命令，并列出需要检查的产物和列名。
