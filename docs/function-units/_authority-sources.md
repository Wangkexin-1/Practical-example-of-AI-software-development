# 权威源登记

日期：2026-10-28；状态：已验证。代码根：C:/Users/ldy/Desktop/检测记录查询工具练习。当前契约为 SPEC-0001 修订 2。

| 编号 | 类/实际绝对代码地址 | 变量与语义、类型 | 单位/坐标 | 初始化/读者/写者 | 持久化、清理与迁移 |
| --- | --- | --- | --- | --- | --- |
| AV-0001 | QuerySession；C:/Users/ldy/Desktop/检测记录查询工具练习/record_query/core.py | data: LoadedData 或 None（source_path:Path、source_identity:tuple[int,int]、records:tuple[Record,...]）；modality/review_status:tuple[str,...] 或 None，枚举顺序规范化且去重。Record 三字段 str；result: Result 派生只读结果 | 无 | 主窗构造初始化；读者 FU-0002/0003、FU-UI-0001；写者 FU-0001/0002 | 不保存会话；FU-0003 只读导出；失败导入或关窗清理；无磁盘结构迁移；旧单字符串调用由 set_filters 适配 |

UI 订阅关系：FU-UI-0001 refresh 读取 data/条件/result，显示路径、行、三项统计和导出可用性。UI 事件只提交 payload，不参与业务计算。

## 2026-10-28 实施与验证补记

代码已实现；tests/test_core.py 的 16 项测试通过，含 42 组筛选与导出往返、输入反例、链接保护与失败清理。具体覆盖见 docs/test-report.md。原计划中“待执行/NOT_RUN”描述为编码前状态，以本补记及测试报告为当前结论。无原始 CSV 修改、无旧结构迁移。

## 修订 2 验证结论

29 项自动化测试通过（19 核心、10 控件/布局），包含 256 组多值组合及原 42 组回归。schema、全部读写者、OR/AND 语义与导出均适配；证据见 docs/test-report.md 文末。原生人工验收 NOT_RUN。
