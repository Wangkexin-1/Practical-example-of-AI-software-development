# 依赖与运行说明

## 环境

- Windows 桌面环境。
- Python 3.11 或更高版本，安装时包含 Tcl/Tk 与 Tkinter。
- Git 用于本地版本管理。
- 计划使用 Python 标准库，无第三方运行依赖，无需联网下载业务库。

本轮准备机器实测：Python 3.14.7、Tk 9.0、Git 2.55.0.windows.3。其他版本尚未验证。

## 首次准备

在项目目录打开 PowerShell；不要在其他项目的虚拟环境中操作：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --no-index -r requirements.txt
.\.venv\Scripts\python.exe scripts\check_environment.py
.\.venv\Scripts\python.exe scripts\verify_samples.py
```

本目录已创建 `.venv` 时，直接执行最后两行即可。虚拟环境不提交 Git；移动目录或换机器后应重新创建。`requirements.txt` 目前只有说明注释，安装步骤不会下载第三方依赖。

Tkinter 不是 pip 包。导入失败时，需要为所使用的 Python 安装补充 Tcl/Tk 组件。

## 当前可执行内容

环境检查脚本报告 Python、Tk 和 Git 版本，只用于环境准备，不验证应用业务或窗口交互。样例检查脚本验证 17 份 CSV 的清单、字节散列、合法/错误数据结构，以及两份答案清单中共 42 种筛选预期；不导入或调用应用代码。

主程序尚未实现，当前没有应用启动命令。后续实现时会在此补充真实入口及测试命令。

## 实现后的操作流程

1. 打开工具并选择 CSV，先用 `samples/original/影像资料复核状态表.csv`。
2. 按 modality 和 review_status 筛选，查看列表和三项统计。
3. 选择新文件路径导出，例如 `exports/待复核.csv`。
4. 使用 `samples/README.md` 与 `samples/expected/` 对照后续验收结果。

## Git

仓库仅保存在本地，不配置远程地址。`.venv`、临时准备工具、缓存及导出文件不提交；输入样例和预期结果纳入版本管理。

```powershell
git status
git log --oneline -5
```
