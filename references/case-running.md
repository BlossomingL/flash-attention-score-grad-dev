# 跑用例流程

当用户要跑 FlashAttentionScoreGrad 用例、根据自然语言描述生成用例表，或指定已有表格和 sheet 执行时，读取本文件。

## 前置输入

先使用 `SKILL.md` 中确认过的全局路径：

- `<OPS_TRANSFORMER_ROOT>`
- `<FAG_TEST_ROOT>`
- `<CANN_PACKAGE_PATH>`

跑用例有两种方式：

- 描述生成：用户给出用例描述，由 Codex 根据 `<FAG_TEST_ROOT>/data` 下表格模板生成新用例表。
- 指定表格：用户给出 case 表路径和 sheet，直接运行该表。

## 方式一：描述生成用例表

适用场景：

- 用户说“帮我生成一个 PSE 场景用例表”。
- 用户描述 shape、layout、dtype、mask、dropout、rope、sink、TND/varlen 等条件，但没有现成表格。
- 用户要基于已有模板扩展一批 case。

流程：

1. 读取 `<FAG_TEST_ROOT>/data` 目录，列出可用模板表。
2. 按描述选择最接近的模板；如果不确定，先问用户选哪个模板。
3. 读取模板的 sheet、表头和代表性数据行。
4. 保留模板列名、sheet 结构和脚本依赖字段，不随意改列名。
5. 生成新表到 `<FAG_TEST_ROOT>/data/generated/` 或用户指定位置。
6. 对新表先跑 `--golden-only` 的 1 到 2 行 smoke。
7. smoke 通过后，再参考 `run_with_pta.sh` 或 `run_with_tilingKey.sh` 跑 NPU 精度/性能。

模板选择建议：

- 优先参考 `FASG.xls` 或通用回归表。
- 用户明确指定模板时，以用户指定模板为准。

生成规则：

- 使用结构化表格读写库，不要用纯字符串拼表。
- `.csv` 优先用 Python `csv` 或 `pandas`。
- `.xlsx` 优先用 `openpyxl`。
- `.xls` 需要确认运行环境是否具备可写库；如果缺少依赖，先复制模板并说明需要用户补齐，或生成 CSV 版本供用户转换。
- 对无法从描述确定的字段，保留模板默认值或写入 `TODO`/显式备注，并在输出中列出不确定项。
- 生成后报告：模板来源、新表路径、sheet、行范围、关键字段映射、不确定字段。

描述生成后的命令模板：

```bash
cd <FAG_TEST_ROOT>
python3 -u run_fag.py --golden-only --case ./data/generated/<case_file> --sheet <sheet> --start-from 1 --end-at 2
bash ./run_with_pta.sh <CANN_PACKAGE_PATH>
```

如果需要先构建指定 tiling_key 算子：

```bash
cd <FAG_TEST_ROOT>
bash ./run_with_tilingKey.sh <CANN_PACKAGE_PATH> <OPS_TRANSFORMER_ROOT> <FAG_TEST_ROOT>
```

## 方式二：指定表格和 Sheet

适用场景：

- 用户给出 case 表路径。
- 用户给出 sheet 名。
- 用户指定行范围或要求跑全表。

需要确认：

- case 表路径：可以是绝对路径，也可以是相对 `<FAG_TEST_ROOT>` 的路径。
- sheet：必须使用用户指定 sheet；如果用户没有指定，先问。
- 行范围：如果用户没有指定，先默认建议小范围 smoke，不直接跑全量。

执行规则：

- 不修改用户指定的原始表格，除非用户明确要求。
- 先跑 `--golden-only` 小范围。
- 再按需求跑 `run_with_pta.sh` 或 `run_with_tilingKey.sh`。
- 如果脚本内写死 `./data/FASG.xls`，而用户指定了别的表，需要先说明脚本可能需要临时参数化或使用等价 `run_fag.py` 命令执行。

指定表格命令模板：

```bash
cd <FAG_TEST_ROOT>
python3 -u run_fag.py --golden-only --case <case_path> --sheet <sheet> --start-from <start> --end-at <end>
python3 -u run_fag.py --case <case_path> --sheet <sheet> --pta --pta_mode=only_grad --device 0 --start-from <start> --end-at <end>
python3 -u run_fag.py --case <case_path> --sheet <sheet> --pta_mode=profiler --device 0 --start-from <start> --end-at <end>
```

## 输出格式

跑用例前输出：

```markdown
## 用例执行计划

- 方式：描述生成 / 指定表格
- ops-transformer仓路径：<OPS_TRANSFORMER_ROOT>
- 测试脚本仓路径：<FAG_TEST_ROOT>
- CANN包路径：<CANN_PACKAGE_PATH>
- case表：<case_path>
- sheet：<sheet>
- 行范围：<start>-<end>
- 验证链路：golden-only / PTA / tilingKey / profiler
```

跑完后输出：

```markdown
## 用例执行结果

- 命令：`...`
- 结果表：`...`
- 日志：`...`
- 结论：通过 / 失败 / 未完成
- 下一步：...
```
