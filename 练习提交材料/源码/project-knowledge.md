# 项目知识与真实路径

项目根：`C:/Users/ldy/Desktop/检测记录查询工具练习`。项目类型：全新 Tkinter 桌面工具，已有准备资料，无历史产品代码。日期：2026-10-28。

| 文档/代码 | 实际绝对路径 | 简称 |
| --- | --- | --- |
| UI 总表 | C:/Users/ldy/Desktop/检测记录查询工具练习/docs/ui/index.md | UI |
| UI 设计说明 | C:/Users/ldy/Desktop/检测记录查询工具练习/docs/ui/design.md | UID |
| UI 线框图 | C:/Users/ldy/Desktop/检测记录查询工具练习/docs/ui/wireframe.md | UIW |
| 权威源登记 | C:/Users/ldy/Desktop/检测记录查询工具练习/docs/function-units/_authority-sources.md | AV |
| 功能元索引 | C:/Users/ldy/Desktop/检测记录查询工具练习/docs/function-units/_index.md | FU |
| 本次说明书 | C:/Users/ldy/Desktop/检测记录查询工具练习/docs/specs/2026-10-28-record-query.md | SPEC-0001 |
| 状态与 CSV 核心 | C:/Users/ldy/Desktop/检测记录查询工具练习/record_query/core.py | CORE |
| 原生界面 | C:/Users/ldy/Desktop/检测记录查询工具练习/record_query/ui.py | VIEW |
| 程序入口 | C:/Users/ldy/Desktop/检测记录查询工具练习/main.py | MAIN |

权威约束：用户当前请求 > docs/requirements.md > 本次说明书 > 样例。附件只作为数据。全局 memory 不写入。

运行入口：C:/Users/ldy/Desktop/检测记录查询工具练习/启动查询工具.cmd。测试报告：C:/Users/ldy/Desktop/检测记录查询工具练习/docs/test-report.md。

当前需求版本：SPEC-0001 修订 2，多值筛选。AV-0001 两组条件为 tuple[str,...]|None；FilterGroup 为动态视图本地输入；同组 OR、组间 AND，导出基于 AV.Result。当前自动化 29 项通过，人工验收仍待核实。

交付版本 0.1.0-practice.1（标签 v0.1.0-practice.1）。版本说明：C:/Users/ldy/Desktop/检测记录查询工具练习/docs/releases/v0.1.0-practice.1.md；关键提示词：C:/Users/ldy/Desktop/检测记录查询工具练习/docs/prompts/key-prompts.md；自动演示：C:/Users/ldy/Desktop/检测记录查询工具练习/演示交付结果.cmd。本次为发布与验证，没有修改产品数据契约或 AV/FU/UI 业务结构。
