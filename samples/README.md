# 样例与预期结果

所有数据仅供练习。`original/影像资料复核状态表.csv` 是用户提供文件的逐字节副本；其余文件为本次自建数据。每个文件的 SHA-256、编码、行数或预期错误见 `expected/manifest.json`。

## 合法输入

| 文件 | 内容与预期 |
| --- | --- |
| original/影像资料复核状态表.csv | 6 条，待复核 3、已复核 3 |
| valid/all_modalities.csv | 18 条，待复核 9、已复核 9，涵盖全部六种 modality |
| valid/all_modalities_bom.csv | 同上，UTF-8 BOM，用于编码兼容性 |
| valid/header_only.csv | 只有表头，0 条，三项统计均为 0 |
| valid/single_record.csv | 1 条 E、待复核 |
| valid/extra_columns.csv | 含 note 额外列，导出只保留必需三列 |
| valid/quoted_fields.csv | record_id 含逗号、双引号、中文，验证 CSV 转义及字段原值 |

主样例使用不同分布，避免各组同数量掩盖错误：

| modality | 总数 | 待复核 | 已复核 |
| --- | ---: | ---: | ---: |
| U | 4 | 3 | 1 |
| V | 3 | 1 | 2 |
| E | 3 | 2 | 1 |
| R | 2 | 0 | 2 |
| C1 | 2 | 2 | 0 |
| C2 | 4 | 1 | 3 |
| 全部 | 18 | 9 | 9 |

`expected/all_modalities_filters.json` 固定记录上述分布对应的 21 种筛选条件、预期 ID 顺序和三项统计。`expected/original_filters.json` 对原样例提供同样的 21 种预期，包括 E 条件零匹配。预期来自固定样例清单，不调用未来的应用筛选代码。

## 错误输入

| 文件 | 预期 |
| --- | --- |
| invalid/missing_record_id.csv | 缺 record_id 列，停止处理 |
| invalid/missing_modality.csv | 缺 modality 列，停止处理 |
| invalid/missing_review_status.csv | 缺 review_status 列，停止处理 |
| invalid/invalid_modality.csv | 第 3 行 modality=X 非法，停止处理，不接收前面的合法行 |
| invalid/invalid_review_status.csv | 第 3 行 review_status=复核中 非法，停止处理 |
| invalid/empty_modality.csv | 第 2 行 modality 为空，停止处理 |
| invalid/empty_review_status.csv | 第 2 行 review_status 为空，停止处理 |
| invalid/not_utf8.csv | GBK 编码，UTF-8 严格解码应失败 |
| invalid/malformed_csv.csv | 引号未闭合，严格 CSV 解析应失败 |
| invalid/empty_file.csv | 零字节，无表头，应报缺少表头/必需列 |

文件缺失测试请指定 `samples/invalid/does_not_exist.csv`，该路径刻意不创建。

本轮仅检查样例本身和预期清单的一致性。应用尚未实现，所有正式功能测试为 NOT_RUN。
