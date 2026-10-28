"""Application entry: python main.py [optional-input.csv]."""

import argparse
import logging
from pathlib import Path
import sys
import tkinter as tk
from tkinter import messagebox

from record_query.ui import QueryWindow


def main():
    parser = argparse.ArgumentParser(description="检测记录查询工具：导入、筛选和导出 UTF-8 CSV")
    parser.add_argument("csv_file", nargs="?", help="可选：启动后打开的 CSV 文件")
    args = parser.parse_args()
    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        filename=log_dir / "application.log", encoding="utf-8", level=logging.ERROR,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    root = tk.Tk()

    def on_callback_error(kind, value, traceback):
        logging.error("Unhandled UI error", exc_info=(kind, value, traceback))
        messagebox.showerror("操作失败", f"发生未预期错误：{value}\n详情已记录到 logs/application.log。", parent=root)

    root.report_callback_exception = on_callback_error
    app = QueryWindow(root)
    if args.csv_file:
        root.after(100, lambda: app.load_path(args.csv_file))
    root.mainloop()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        logging.exception("Application startup failed")
        print("启动失败，请检查 Python/Tkinter 环境及 logs/application.log。", file=sys.stderr)
        raise
