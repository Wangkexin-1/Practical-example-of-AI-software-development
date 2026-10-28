# 依赖与运行说明

适用交付版本：0.1.0-practice.1，标签 v0.1.0-practice.1。

## 环境

- Windows 桌面环境。
- Python 3.11 或更高版本，安装时包含 Tcl/Tk 与 Tkinter。
- Git 用于本地版本管理。
- 使用 Python 标准库，无第三方运行依赖，无需联网下载业务库。

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

主程序运行只需要 Python/Tk；Git 是仓库与开发环境检查所需工具。源码 ZIP 不包含 `.venv`，解压后在新项目目录重新创建，不复制旧虚拟环境。

## 启动查询工具

**推荐：双击项目根目录的 `启动查询工具.cmd`。** 入口先使用项目 `.venv`，没有虚拟环境时尝试系统 Python 或 py 启动器；失败时保留命令窗口显示原因。

在任意工作目录也可以通过入口完整路径启动，入口自动切换到项目目录。

在项目目录使用 PowerShell 启动：

```powershell
.\.venv\Scripts\python.exe main.py
```

启动时直接打开原样例：

```powershell
.\.venv\Scripts\python.exe main.py "samples\original\影像资料复核状态表.csv"
```

关闭主窗口即退出应用。正常启动不需要联网、管理员权限或安装第三方包。未预期错误记录到项目 `logs/application.log`。

## 现场演示交付

双击根目录 `演示交付结果.cmd`，直接打开 `samples/valid/all_modalities.csv`，使用原 main.py 入口，无额外自动测试。

1. 初始 18/9/9。
2. modality 选 U，再增加框选 V，显示 7/4/3。
3. review_status 选待复核，显示 4/4/0。
4. 导出新文件，应为 S001、S002、S003、S005。
5. 状态再增加已复核，显示 7/4/3；重置恢复 18/9/9。

截图、已产生的 CSV 输出及测试证据在 `docs/releases/evidence/v0.1.0-practice.1/`。用户已反馈运行结果正确，并要求停止继续测试，本次据此完成版本收尾。原生全流程自动化未完成，不记作通过。

## 检查命令

环境检查脚本报告 Python、Tk 和 Git 版本，只用于环境准备，不验证应用业务或窗口交互。样例检查脚本验证 17 份 CSV 的清单、字节散列、合法/错误数据结构，以及两份答案清单中共 42 种筛选预期；不导入或调用应用代码。

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

这是专门的功能测试，临时输出写入自动清理的临时目录，不覆盖项目输入。测试需要可用 Tk 桌面环境；符号链接能力不可用时该项显示 skipped，不能据此宣称通过。本次修订在本机器 29 项均通过，无 skipped。

## 操作流程

1. 打开工具并选择 CSV，先用 `samples/original/影像资料复核状态表.csv`。
2. 两组各可点“+ 增加条件”增加下拉框，选项排除同组其他框已选值；可“移除”。同组按“或”、两组按“且”匹配，查看列表和三项统计。
3. 选择新文件路径导出，例如 `exports/待复核.csv`。
4. 使用 `samples/README.md` 与 `samples/expected/` 对照后续验收结果。

原样例预期：全部为 6/3/3；modality=U 为 2/1/1；再加待复核为 1/1/0，记录为 R001。modality=E 为零条，仍可导出表头。“全部”不是业务枚举，只代表取消该项限制。

多选示例：原样例 modality=U、V 为 3/1/2，再加 review_status=待复核为 1/1/0；再加入已复核则回到 3/1/2。主样例 modality=U、V 且待复核为 4/4/0，记录 S001、S002、S003、S005。

新增的“请选择”空框不影响结果，不会自动选中。模态最多 6 框、状态最多 2 框；已选项更换或移除后可重新选择。重置、重新导入及导入失败恢复每组一个“全部”；取消导入不清理选择。增加较多行时窗口最小高度相应增长，避免遮住表格或导出按钮。

导出要求选择新文件名；现有输出也不会覆盖。文件选择或保存对话框点取消不改变查询。导入实际失败则清空旧数据并禁用导出，重新导入合法文件即可继续。

## Git

仓库仅保存在本地，不配置远程地址。`.venv`、临时准备工具、缓存及导出文件不提交；输入样例和预期结果纳入版本管理。

```powershell
git status
git log --oneline -5
```
