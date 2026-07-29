# 开发流程

当进行 FlashAttentionScoreGrad 日常源码修改时，读取本文件。

## 编辑前

1. 确认目标源码树为用户输入的 `<OPS_TRANSFORMER_ROOT>`。
2. 在目标仓库执行 `git status --short`，确认已有未提交变更。
3. 围绕路径选择、tiling key、dtype/layout 分支或功能开关做窄范围搜索。
4. 修改 tiling/kernel 前，记录失败或目标用例 shape。

常用命令：

```bash
rg -n "flash_attention_score_grad|FlashAttentionScoreGrad|FAG" <OPS_TRANSFORMER_ROOT>/attention/flash_attention_score_grad
rg -n "TND|BNSD|pse|dropout|rope|sink|deterministic|tilingKey" <OPS_TRANSFORMER_ROOT>/attention/flash_attention_score_grad/op_host <OPS_TRANSFORMER_ROOT>/attention/flash_attention_score_grad/op_kernel
```

搜索范围优先限制在 `<OPS_TRANSFORMER_ROOT>` 和 `<FAG_TEST_ROOT>`，不要扫描无关目录。

## 修改策略

修改 op_api/op_graph：

- 检查共享该参数的版本化文档和 examples。
- 只有接口契约要求时，才同步 V2/V3/V4 和 unpadding 变体。
- 用最小 example 或 harness 用例验证改动过的接口。

修改 op_host/tiling：

- 先判断用例是普通 BNSD 类路径还是 TND/varlen 路径。
- 优先检查架构相关分支，Ascend950/regbase 通常看 `arch35`。
- 保持 tiling data 布局与 `op_kernel/arch*/flash_attention_score_grad_tiling*.h` 消费端一致。
- 编辑后，如果有硬件，至少跑 golden-only 和一个 NPU smoke；涉及指定 tiling_key 时，优先参考 `<FAG_TEST_ROOT>/run_with_tilingKey.sh` 的构建、安装、profiling 链路。

修改 op_kernel：

- 从选中的 tiling key 和 kernel entry 路径出发。
- 如果 `dq/dk/dv` 全部偏移，检查 cube/vector 共享阶段；如果只有一个输出失败，先查对应输出路径。
- deterministic 用例要单独检查 deterministic 代码。
- 涉及 PSE/mask/dropout/rope/sink 时，先查对应功能模块，再改公共数学逻辑。

修改调试工具：

- 保持 `CaseConfig` 解析、golden 生成、NPU 执行、结果比较职责分离。
- 修改随机输入、PSE/mask 语义、dtype 转换或 layout transform 后，不要复用过期 `--cache-data`。
- 优先在可疑分支增加聚焦断言或日志，不要默认 dump 大量 tensor。

## 验证阶梯

使用覆盖风险的最低成本验证：

```bash
cd <FAG_TEST_ROOT>
python3 -u ./run_fag.py --golden-only --case ./data/FASG.xls --sheet Sheet1 --start-from 1 --end-at 2
python3 -u ./run_fag.py --case ./data/FASG.xls --sheet Sheet1 --pta --pta_mode=only_grad --device 0 --start-from 1 --end-at 2
```

smoke 通过后再扩大：

```bash
python3 -u ./run_fag.py --case ./data/FASG_David.xls --sheet Sheet1 --pta --pta_mode=only_grad --device 0 --start-from 1 --end-at -1
python3 -u ./run_fag.py --case ./data/FASG_TND1.xls --sheet Sheet1 --pta --pta_mode=only_grad --device 0 --start-from 1 --end-at -1
python3 -u ./run_fag.py --case ./data/FASG_PSE_cases.csv --sheet Sheet1 --pta --pta_mode=only_grad --device 0 --start-from 1 --end-at -1
```

验证后报告：

- 目标仓库/目录和修改文件。
- case 文件、sheet、行范围、命令。
- 新结果文件和 `run_log.txt` 中的关键证据。
- 是否实际运行 NPU 验证；如果不能运行，只说明完成了 golden/脚本级验证。
