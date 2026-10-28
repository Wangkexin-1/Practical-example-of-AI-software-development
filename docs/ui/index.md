# UI 总表

状态：待核实；日期：2026-10-28。项目根与代码绝对路径见 project-knowledge.md。

| 条款 | 控件/触发 FU | 订阅 AV | 服务关系 |
| --- | --- | --- | --- |
| UI-01 | 导入 CSV、Ctrl+O → FU-0001 | AV-0001 data/源路径 | FU-UI-0001 ↔ FU-0001 |
| UI-02 | modality/review_status 下拉、重置 → FU-0002 | AV-0001 条件/result/统计 | FU-UI-0001 ↔ FU-0002 |
| UI-03 | 导出 CSV、Ctrl+E → FU-0003 | AV-0001 data 是否有效 | FU-UI-0001 ↔ FU-0003 |

设计与线框：design.md、wireframe.md。来源说明书：docs/specs/2026-10-28-record-query.md。

## 2026-10-28 实施补记

代码、启动入口和说明已落盘；20 项自动化测试通过，实际启动窗口已加载原样例并保存截图。核心 FU-0001/0002/0003 已验证，AV-0001 已验证；FU-UI-0001 及任务整体待核实（完整原生键鼠流程与人工验收未完成）。具体证据及 NOT_RUN 边界以 docs/test-report.md 为准。
