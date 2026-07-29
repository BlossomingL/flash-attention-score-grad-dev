# 性能分析流程

当用户询问 kernel time、profiler 模式、op_summary、慢用例、性能回退对比、cube/vector 瓶颈或性能优化时，读取本文件。

如果用户要先生成性能用例表，或指定 case 表和 sheet 跑 profiler，先读取 `case-running.md`。

## 运行 profiler 模式

性能验证优先参考 `<FAG_TEST_ROOT>/run_with_pta.sh` 和 `<FAG_TEST_ROOT>/run_with_tilingKey.sh`。

执行前先让用户选择运行模式：无需编译直接跑，或先构建指定 tiling_key 再跑。

直接 PTA profiling：

```bash
cd <FAG_TEST_ROOT>
bash ./run_with_pta.sh <CANN_PACKAGE_PATH>
```

指定 tiling_key 构建、安装并 profiling：

```bash
cd <FAG_TEST_ROOT>
bash ./run_with_tilingKey.sh <CANN_PACKAGE_PATH> <OPS_TRANSFORMER_ROOT> <FAG_TEST_ROOT>
```

`run_with_tilingKey.sh` 的核心动作：

- 设置 `CANN_PATH=$1`、`CODE_PATH=$2`、`TEST_PATH=$3`。
- `source <CANN_PACKAGE_PATH>/cann/bin/setenv.bash`。
- 在 `<OPS_TRANSFORMER_ROOT>` 执行 `bash build.sh --pkg --ops="flash_attention_score_grad" --soc=ascend950 --tiling_key="19843988006114480"`。
- 检查并安装 `build/cann-ops-transformer-custom_linux-x86_64.run` 到 `<CANN_PACKAGE_PATH>`。
- `source <CANN_PACKAGE_PATH>/vendors/custom_transformer/bin/set_env.bash`。
- 在 `<FAG_TEST_ROOT>` 通过 `msprof --output=./profiling` 执行 `run_fag.py`，再执行 `show_prof.py`。

需要临时绕开脚本时，在 `<FAG_TEST_ROOT>` 下执行：

```bash
python3 -u ./run_fag.py --case ./data/FASG.xls --sheet Sheet1 --pta_mode=profiler --device 0 --start-from 1 --end-at 2
```

按类别运行：

```bash
python3 -u ./run_fag.py --case ./data/FASG_David.xls --sheet Sheet1 --pta_mode=profiler --device 0 --start-from 1 --end-at -1
python3 -u ./run_fag.py --case ./data/FASG_TND1.xls --sheet Sheet1 --pta_mode=profiler --device 0 --start-from 1 --end-at -1
python3 -u ./run_fag.py --case ./data/FASG_PSE_cases.csv --sheet Sheet1 --pta_mode=profiler --device 0 --start-from 1 --end-at -1
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

```bash
ls -t ./results/FlashAttentionScoreGrad_Result_* | head -5
tail -n 200 ./run_log.txt
python3 ./fag_test/show_prof.py --help
```

依赖 `show_prof.py` 的参数前，先阅读 `<FAG_TEST_ROOT>` 下的脚本，保证命令示例与实际 CLI 一致。

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
- 如用户提供了额外性能分析笔记，可作为背景材料；修改代码前仍以 `<OPS_TRANSFORMER_ROOT>` 中源码为准。

## 输出报告

说明数字来源：profiler 模式、结果表 kernel time，还是日志推断。包含精确命令和结果产物。如果当前执行环境不能运行，给出应在 NPU 环境执行的命令，并列出需要检查的产物和列名。
