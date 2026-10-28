# 检测记录查询工具练习

练习交付版本：**0.1.0-practice.1**；Git 标签：`v0.1.0-practice.1`。变更见 [CHANGELOG.md](CHANGELOG.md)，交付清单见 [版本说明](docs/releases/v0.1.0-practice.1.md)，关键提示词见 [提示词归档](docs/prompts/key-prompts.md)。

已实现 UTF-8 CSV 导入校验、筛选统计和结果导出，无第三方运行依赖。

## 运行入口

**双击本目录的 `启动查询工具.cmd`。** 当前机器已准备好 `.venv`，可以直接使用。

也可在本目录打开 PowerShell：

```powershell
.\.venv\Scripts\python.exe main.py
```

带文件参数可直接加载样例：

```powershell
.\.venv\Scripts\python.exe main.py "samples\original\影像资料复核状态表.csv"
```

## 交付演示

双击 **`演示交付结果.cmd`**，直接打开含 18 条记录的主样例。先选 modality=U，再“增加条件”选 V，显示 7/4/3；review_status 选待复核，显示 4/4/0；导出新 CSV 应为 S001、S002、S003、S005。复核状态再增加已复核，恢复 7/4/3。点重置恢复 18/9/9。

现场演示图和输出保存在 `docs/releases/evidence/v0.1.0-practice.1/`。用户已查看运行结果并反馈正确；按用户要求停止继续测试。源码 ZIP 不带 `.venv`，解压后按运行说明准备环境。

## 使用

1. 点击“导入 CSV”（Ctrl+O）选择 UTF-8 文件，支持 UTF-8 BOM。
2. 在 modality、review_status 各自的下拉框选择条件；点击该组“+ 增加条件”可再选一个值，其他框中已选的内容不会重复出现。可点击“移除”删除一项。
3. 同一组多个值按“或”匹配，两组之间按“且”匹配。例如 modality 选 U、V，review_status 选待复核，会显示 U 或 V 的待复核记录。新增框“请选择”不参与筛选；“重置筛选”恢复每组一个“全部”。
4. 查看结果表格及总数、待复核数、已复核数。
5. 点击“导出 CSV”（Ctrl+E），选择一个新文件名。输出为 UTF-8 BOM CSV，方便 Excel 读取中文，只保留三列及表头。

模态最多 6 个框，复核状态最多 2 个框，到达上限后增加按钮禁用。选项更换或移除后会重新出现在其他框中。增加较多筛选行时窗口会按需增高，保留表格和导出按钮。

文件缺失、缺列、非法枚举、编码或 CSV 格式错误均弹窗说明并停止本次导入，清空旧查询。选择文件时取消则保留原查询。已有文件一律不会覆盖，请更换导出名称。合法空表和零匹配都能导出仅有表头的 CSV。

本目录是独立练习项目；样例、说明、环境与本地 Git 仓库均位于本目录。

## 当前内容

- `samples/original/`：用户原始 CSV 的逐字节副本。
- `samples/valid/`：合法、空表、BOM、额外列、带引号字段样例。
- `samples/invalid/`：缺列、非法枚举、错误编码、损坏格式等反例。
- `samples/expected/`：筛选预期记录与统计、样例校验清单。
- `docs/requirements.md`：当前需求基准与后续开发顺序。
- `docs/run.md`：环境准备、检查及未来软件操作流程。
- `docs/preparation-check.md`：本轮准备检查结果与验收边界。
- `docs/test-report.md`：功能测试结果与实际启动证据。
- `docs/specs/`、`docs/function-units/`、`docs/ui/`：功能说明书、数据与界面档案。
- `record_query/`、`main.py`：应用源代码。
- `tests/`：业务及控件级集成测试。
- `scripts/check_environment.py`：可重复执行的环境检查。
- `requirements.txt`：依赖说明，目前没有第三方运行依赖。
- `exports/`：预留导出目录，生成的 CSV 不纳入 Git。
- `dev-log/`：每日操作记录。
- `VERSION`、`CHANGELOG.md`、`docs/prompts/`、`docs/releases/`：版本、变更、关键提示词和发布记录。
- `演示交付结果.cmd`：直接打开主样例的现场演示入口。
- `deliveries/`：由 Git 标签生成的源码 ZIP、Git bundle、清单与校验文件，不纳入 Git。

## 可重复检查

在本目录打开 PowerShell：

```powershell
.\.venv\Scripts\python.exe scripts\check_environment.py
.\.venv\Scripts\python.exe scripts\verify_samples.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

新机器没有 `.venv` 时，按 `docs/run.md` 创建。无需激活环境，也无需修改 PowerShell 执行策略。

检查结果：29 项自动化测试通过，包含 256 组多值条件、原固定 42 组筛选预期、候选排除与回补、最大行数布局及 CSV 导出往返；新版运行入口已实际启动并加载原样例。完整原生键鼠流程及人工验收尚未完成，详见 `docs/test-report.md`。新机器的环境准备见 `docs/run.md`。

## GitHub 公开提交材料

目标公开仓库：https://github.com/Wangkexin-1/Practical-example-of-AI-software-development 。

- 完整练习提交目录：[练习提交材料](练习提交材料/提交清单与入口.md)
- 可直接下载的完整压缩包：[练习提交材料.zip](练习提交材料.zip)
- 全部任务提示词：[汇总文档](练习提交材料/全部提示词汇总.md)
- 测试记录：[发布验证说明](docs/releases/verification.md)
- 练习版本标签：`v0.1.0-practice.1`，发布提交 `37db4561d623e098aef0ffaf1bca93955dd48eca`。

仓库根目录提供源码和运行入口，提交材料目录是该练习标签的完整归档；发布标签不随上传文档提交移动。源码与样例可以公开访问，不包含虚拟环境、凭据、缓存或临时日志。用户要求停止测试后未重新运行测试。

目标仓库原始初始化 README 已保存在 [docs/github-initial-readme.md](docs/github-initial-readme.md)，初始化提交历史完整保留。
