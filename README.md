# 检测记录查询工具练习

状态：开发准备完成，查询界面与业务代码尚未实现。

本目录是独立练习项目；样例、说明、环境与本地 Git 仓库均位于本目录。

## 当前内容

- `samples/original/`：用户原始 CSV 的逐字节副本。
- `samples/valid/`：合法、空表、BOM、额外列、带引号字段样例。
- `samples/invalid/`：缺列、非法枚举、错误编码、损坏格式等反例。
- `samples/expected/`：筛选预期记录与统计、样例校验清单。
- `docs/requirements.md`：当前需求基准与后续开发顺序。
- `docs/run.md`：环境准备、检查及未来软件操作流程。
- `docs/preparation-check.md`：本轮准备检查结果与验收边界。
- `scripts/check_environment.py`：可重复执行的环境检查。
- `requirements.txt`：依赖说明，目前没有第三方运行依赖。
- `exports/`：预留导出目录，生成的 CSV 不纳入 Git。
- `dev-log/`：每日操作记录。

## 现在可以运行的检查

在本目录打开 PowerShell：

```powershell
.\.venv\Scripts\python.exe scripts\check_environment.py
.\.venv\Scripts\python.exe scripts\verify_samples.py
```

新机器没有 `.venv` 时，按 `docs/run.md` 创建。无需激活环境，也无需修改 PowerShell 执行策略。

第二条命令检查样例及预期清单的一致性。当前没有应用入口，不能启动查询窗口；后续开发完成后补充真实启动命令。样例文件已准备，不代表软件功能已通过验收。
