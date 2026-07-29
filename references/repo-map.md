# 仓库地图

当需要定位 FlashAttentionScoreGrad 实现、测试、生成产物或已有分析笔记时，读取本文件。

## 主要工作区

- `fag_debug_tools/`：日常 golden 生成、NPU 执行、精度比较、结果表、日志和 profiler 展示工具。
- `ops-transformer/attention/flash_attention_score_grad/`：当前工作区主算子目录，同时包含 `.understand-operator/` 和 `.testcase-generator/` 产物。
- `ops-transformer-drop/attention/flash_attention_score_grad/`：完整源码镜像，包含 docs、examples、op_api、op_graph、op_host、op_kernel。
- `ops-transformer-smallds/attention/flash_attention_score_grad/`：small-D/S 镜像。
- `ops-transformer-smallds-gpt/attention/flash_attention_score_grad/`：存在时表示 GPT/small-D/S 变体。
- `ops-transformer-tiling/attention/flash_attention_score_grad/`：tiling 侧重点镜像。

编辑前要根据用户请求、当前 git 分支或已有变更确认目标目录。

## 算子源码结构

每个 `attention/flash_attention_score_grad` 目录通常包含：

- `docs/`：ACLNN 接口文档和设计说明。
- `examples/`：独立 ACLNN 样例，包括 V2/V4/fp16/fp32/sparse/varlen。
- `op_api/`：ACLNN 和 wrapper 接口实现。
- `op_graph/`：graph proto/plugin 声明。
- `op_host/`：infer shape、tiling 定义、架构相关 tiling。
- `op_host/arch22/`：较老架构 tiling 策略。
- `op_host/arch35/`：regbase/Ascend950 风格 tiling 策略。
- `op_kernel/`：kernel 入口和架构相关 kernel 实现。
- `op_kernel/arch35/`：regbase kernel 路径、block cube/vector、template tiling key、deterministic、vector API、cube API。
- `CMakeLists.txt`：构建集成。

常见 arch35 调试文件：

- `op_host/arch35/flash_attention_score_grad_tiling_common_regbase.*`
- `op_host/arch35/flash_attention_score_grad_tiling_normal_regbase.*`
- `op_host/arch35/flash_attention_score_grad_tiling_varlen_regbase.cpp`
- `op_kernel/arch35/flash_attention_score_grad_kernel*.h`
- `op_kernel/arch35/flash_attention_score_grad_block_cube.h`
- `op_kernel/arch35/flash_attention_score_grad_block_vec.h`
- `op_kernel/arch35/flash_attention_score_grad_template_tiling_key.h`
- `op_kernel/arch35/vector_api/*.h`
- `op_kernel/arch35/cube_api/*.h`

## 调试工具结构

`fag_debug_tools/`：

- `run_fag.py`：顶层可执行入口。
- `requirements.txt`：Python 依赖。
- `data/`：Excel/CSV 用例表，如 `FASG.xls`、`FASG_David.xls`、`FASG_TND1.xls`、`FASG_PSE_cases.csv`。
- `auto_input/`：生成的输入和 golden `.pt`/`.npy` 产物。
- `results/`：`FlashAttentionScoreGrad_Result_<timestamp>.*` 输出表。
- `run_log.txt`：追加写入的运行日志。
- `docs/debug_notes.md`：历史问题记录。
- `docs/pse_shapes.md`：PSE shape/type 定义和支持矩阵。
- `fag_test/config.py`：运行时和用例配置。
- `fag_test/golden.py`：普通和 flash golden 数学逻辑。
- `fag_test/pipeline.py`：输入/golden 生成流水线。
- `fag_test/runner.py`：NPU 调用、结果检查、profiler 写入。
- `fag_test/test_utils.py`：用例解析、日志、比较。
- `fag_test/show_prof.py`：profiler summary 展示。

## 本地分析笔记

当前工作区内可参考的顶层笔记：

- `flash_attn_code_structure_analysis.md`
- `buffer_allocation_analysis.md`
- `cube_scalar_optimization_plan.md`
- `small_s_small_d_low_scalar_template_design.md`
- `REFACTOR_PLAN.md`
- `fag.md`
- `fag_metadata.md`

这些文件只作为背景材料。修改代码前必须回到当前源码核对。
