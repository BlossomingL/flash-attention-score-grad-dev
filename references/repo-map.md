# 仓库地图

当需要定位 FlashAttentionScoreGrad 实现、测试、生成产物或已有分析笔记时，读取本文件。

先使用 `SKILL.md` 中确认过的全局路径：

- `<OPS_TRANSFORMER_ROOT>`：用户输入的 ops-transformer 仓路径。
- `<FAG_TEST_ROOT>`：用户输入的测试脚本仓路径。
- `<CANN_PACKAGE_PATH>`：用户输入的 CANN 包路径。

本文件中的相对路径说明只用于识别目录结构。实际读写、搜索、运行命令时，必须把路径解析到用户输入的全局路径下。

## 主要工作区

- `<FAG_TEST_ROOT>/`：日常 golden 生成、NPU 执行、精度比较、结果表、日志和 profiler 展示工具。
- `<OPS_TRANSFORMER_ROOT>/attention/flash_attention_score_grad/`：用户确认的主算子目录，可能包含 `.understand-operator/` 和 `.testcase-generator/` 产物。
如果用户提供了多个候选仓库，先让用户明确本次使用哪一个作为 `<OPS_TRANSFORMER_ROOT>`。

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
- `run_with_pta.sh`：日常 PTA 精度/性能调测脚本，参数为 `<CANN_PACKAGE_PATH>`。
- `run_with_tilingKey.sh`：日常指定 tiling_key 构建、安装、profiling 脚本，参数为 `<CANN_PACKAGE_PATH> <OPS_TRANSFORMER_ROOT> <FAG_TEST_ROOT>`。
- `requirements.txt`：Python 依赖。
- `data/`：Excel/CSV 用例表模板。生成新用例表时，先读取该目录下现有表格的列、sheet 和示例行，再按模板生成。
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

如果用户提供了额外分析笔记，只作为背景材料。修改代码前必须回到 `<OPS_TRANSFORMER_ROOT>` 中的目标源码核对。
