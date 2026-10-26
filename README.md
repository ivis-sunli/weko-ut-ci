# WEKO UT CI

独立于 WEKO 主仓库的单次单元测试工作流。手动运行 Actions 中的 **WEKO unit tests**，在 `config_file` 中填写 `config/` 下的 JSON 文件名，默认 `modules.json`。工作流并行测试该配置中的全部模块，汇总报告使用同一份清单。

默认的 [模块清单](config/modules.json) 包含 46 个模块。每个模块分别指定仓库、分支和可选的 commit：

```json
[
  {
    "module": "invenio-accounts",
    "repository": "ivis-sunli/weko",
    "branch": "fix/W2026-31_ut_invenio-accounts",
    "commit": ""
  }
]
```

`module`、`repository`（`owner/repo`）和 `branch` 必填。`commit` 可省略、设为 `null` 或留空，均检出指定分支的最新 HEAD；填写 commit SHA 时优先检出该提交。每份清单中的模块名不能重复，仓库需要包含现有测试脚本使用的 WEKO 目录结构。

例如，把另一组模块配置保存为 `config/regression.json`，启动时将 `config_file` 填为 `regression.json`，即可按该文件整体测试。

所有模块结束后，下载 **unit-test-report** artifact。其中包含 `index.html`、`summary.csv`、`build/image-build.log` 和 `raw/<模块名>/` 下各模块的镜像构建日志、执行日志、服务日志、JUnit、覆盖率与测试自产生的证据文件。成功和失败的输出一起保存；缺失或未完成的结果不会记作通过。模块失败会保留失败状态，其余模块继续运行。手动取消 workflow 时停止后续汇总。

`summary.csv` 每个模块一行，包含以下列：

| 字段 | 含义 |
|---|---|
| `module` | 模块名，与所选配置文件中的 `module` 一致 |
| `status` | 汇总状态：`passed`（通过）、`failed`（失败）或 `incomplete`（结果不完整） |
| `tests` | JUnit 报告记录的测试总数，包含跳过项 |
| `failures` | JUnit 报告记录的测试失败数 |
| `errors` | JUnit 报告记录的错误数，通常为测试准备或清理阶段的错误 |
| `skipped` | JUnit 报告记录的跳过数 |
| `percent_covered` | coverage.py 综合覆盖率（启用分支覆盖时包含语句与分支） |
| `percent_statements_covered` | 语句覆盖率 |
| `percent_branches_covered` | 分支覆盖率 |

`passed` 要求退出码为 0、JUnit 测试总数大于 0，且失败数和错误数均为 0。非零退出码或有效 JUnit 报告不满足通过条件时记为 `failed`；JUnit 无法解析，或关键结果缺失且无法判定失败时记为 `incomplete`。

测试计数取自 `junit.xml`，覆盖率取自 `coverage.json` 的 `totals`。语句或分支覆盖率百分比缺失时，按对应覆盖计数计算。百分比范围为 0–100；无法取得的字段为空。HTML 汇总展示相同列。
