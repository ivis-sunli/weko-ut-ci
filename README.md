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

一个构建 job 统一构建 runner 和 OpenSearch 插件镜像，通过 `docker save` 导出为压缩包，并上传为 `test-images` artifact（保留一天）。各模块测试 job 下载该包、用 `docker load` 导入镜像，启动 PostgreSQL、Redis、RabbitMQ 和 OpenSearch，然后执行完整的 `c1`：

```bash
python -m tox -e c1 -- tests --tb=short \
  -o console_output_style=progress-even-when-capture-no
```

统一显示测试完成百分比，包括模块自身使用 `-s` 实时输出日志的情况。

镜像每次 workflow 只构建一次，不发布到镜像仓库；各模块仍在自己的分支源码上创建和安装 `c1`。测试环境保留 Python 3.12 安装兼容处理，以及 `instance.cfg` 末尾多余引号的修正；这些处理作用于任务内的临时检出目录。

所有模块结束后，下载 **unit-test-report** artifact。其中包含 `index.html`、`summary.csv`、`build/image-build.log` 和 `raw/` 下各模块的执行日志、服务日志、JUnit、覆盖率与测试自产生的证据文件。成功和失败的输出一起保存；缺失或未完成的结果不会记作通过。模块失败会保留失败状态，其余模块继续运行。手动取消 workflow 时停止后续汇总。

Action 使用稳定版本标签。没有样本模式、镜像发布工作流、资源限制、审计清单或脚本测试。

也可以使用 GitHub CLI 启动：

```bash
gh workflow run unit-tests.yml --ref main -f config_file=modules.json
```
