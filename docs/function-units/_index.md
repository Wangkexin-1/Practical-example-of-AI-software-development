# 功能元索引

需求组 SPEC-0001；状态：待核实；创建日 2026-10-28；核实日：无。

| 编号 | 名称/类型 | 实现地址（项目根下） | 依赖/条款/终点 | 档案 |
| --- | --- | --- | --- | --- |
| FU-0001 | CSV 接入/业务 | record_query/core.py:QuerySession.load,read_records | AV-0001、UI-01；AV 写回/错误 | FU-0001.md |
| FU-0002 | 筛选统计/业务 | record_query/core.py:QuerySession.set_filters,result | AV-0001、UI-02；展示 | FU-0002.md |
| FU-0003 | 结果导出/业务 | record_query/core.py:QuerySession.export | AV-0001、UI-03；新 CSV | FU-0003.md |
| FU-UI-0001 | 主窗口/UI | record_query/ui.py:QueryWindow | AV-0001、UI-01/02/03；窗口 | FU-UI-0001.md |

实际绝对代码地址以 project-knowledge.md 和各档案为准。

## 2026-10-28 实施补记

代码、启动入口和说明已落盘；20 项自动化测试通过，实际启动窗口已加载原样例并保存截图。核心 FU-0001/0002/0003 已验证，AV-0001 已验证；FU-UI-0001 及任务整体待核实（完整原生键鼠流程与人工验收未完成）。具体证据及 NOT_RUN 边界以 docs/test-report.md 为准。
