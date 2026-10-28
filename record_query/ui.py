"""Tkinter view and user event endpoints (FU-UI-0001)."""

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .core import HEADERS, MODALITIES, REVIEW_STATUSES, QueryError, QuerySession


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ALL = "全部"


class QueryWindow:
    def __init__(self, root):
        self.root = root
        self.session = QuerySession()
        root.title("检测记录查询工具")
        root.geometry("960x620")
        root.minsize(740, 460)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        style = ttk.Style(root)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Treeview", rowheight=29)
        style.configure("Title.TLabel", font=("Microsoft YaHei UI", 16, "bold"))
        style.configure("Count.TLabel", font=("Microsoft YaHei UI", 11))

        self.path_text = tk.StringVar(value="尚未导入文件")
        self.modality_text = tk.StringVar(value=ALL)
        self.review_text = tk.StringVar(value=ALL)
        self.total_text = tk.StringVar()
        self.pending_text = tk.StringVar()
        self.reviewed_text = tk.StringVar()
        self.status_text = tk.StringVar(value="请选择 UTF-8 CSV 文件开始查询。")

        frame = ttk.Frame(root, padding=18)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(4, weight=1)
        ttk.Label(frame, text="检测记录查询", style="Title.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 15)
        )

        source = ttk.Frame(frame)
        source.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        source.columnconfigure(1, weight=1)
        self.import_button = ttk.Button(source, text="导入 CSV (Ctrl+O)", command=self.open_file)
        self.import_button.grid(row=0, column=0, padx=(0, 12))
        self.path_entry = ttk.Entry(source, textvariable=self.path_text, state="readonly")
        self.path_entry.grid(row=0, column=1, sticky="ew")

        filters = ttk.Frame(frame)
        filters.grid(row=2, column=0, sticky="w", pady=(0, 15))
        ttk.Label(filters, text="modality：").grid(row=0, column=0, sticky="w")
        self.modality_combo = ttk.Combobox(
            filters, textvariable=self.modality_text, values=(ALL, *MODALITIES),
            state="readonly", width=12,
        )
        self.modality_combo.grid(row=0, column=1, padx=(0, 22))
        ttk.Label(filters, text="review_status：").grid(row=0, column=2, sticky="w")
        self.review_combo = ttk.Combobox(
            filters, textvariable=self.review_text, values=(ALL, *REVIEW_STATUSES),
            state="readonly", width=12,
        )
        self.review_combo.grid(row=0, column=3, padx=(0, 22))
        self.reset_button = ttk.Button(filters, text="重置筛选", command=self.reset_filters)
        self.reset_button.grid(row=0, column=4)
        for combo in (self.modality_combo, self.review_combo):
            combo.bind("<<ComboboxSelected>>", self.apply_filters)

        counts = ttk.Frame(frame)
        counts.grid(row=3, column=0, sticky="ew", pady=(0, 12))
        for index, variable in enumerate((self.total_text, self.pending_text, self.reviewed_text)):
            ttk.Label(counts, textvariable=variable, style="Count.TLabel").grid(
                row=0, column=index, sticky="w", padx=(0, 45)
            )

        table = ttk.Frame(frame)
        table.grid(row=4, column=0, sticky="nsew")
        table.columnconfigure(0, weight=1)
        table.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(table, columns=HEADERS, show="headings", selectmode="extended")
        for name, width in zip(HEADERS, (350, 200, 240)):
            self.tree.heading(name, text=name, anchor="w")
            self.tree.column(name, width=width, minwidth=140, anchor="w")
        vertical = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        horizontal = ttk.Scrollbar(table, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")

        actions = ttk.Frame(frame)
        actions.grid(row=5, column=0, sticky="ew", pady=(14, 10))
        self.export_button = ttk.Button(actions, text="导出 CSV (Ctrl+E)", command=self.export_file)
        self.export_button.grid(row=0, column=0, sticky="w")
        ttk.Label(actions, text="导出为新文件，保留三列及表头").grid(row=0, column=1, padx=16)
        ttk.Label(frame, textvariable=self.status_text, wraplength=880).grid(
            row=6, column=0, sticky="w"
        )

        root.bind("<Control-o>", self.open_file)
        root.bind("<Control-e>", self.export_file)
        root.protocol("WM_DELETE_WINDOW", root.destroy)
        self.refresh()
        self.import_button.focus_set()

    def refresh(self):
        data = self.session.data
        result = self.session.result
        self.path_text.set(str(data.source_path) if data else "尚未导入文件")
        self.modality_text.set(self.session.modality or ALL)
        self.review_text.set(self.session.review_status or ALL)
        self.total_text.set(f"总数：{result.total}")
        self.pending_text.set(f"待复核：{result.pending}")
        self.reviewed_text.set(f"已复核：{result.reviewed}")
        children = self.tree.get_children()
        if children:
            self.tree.delete(*children)
        for row in result.records:
            self.tree.insert("", "end", values=(row.record_id, row.modality, row.review_status))
        self.export_button.configure(state="normal" if data is not None else "disabled")

    def open_file(self, _event=None):
        directory = self.session.data.source_path.parent if self.session.data else PROJECT_ROOT / "samples/original"
        selected = filedialog.askopenfilename(
            parent=self.root, title="选择检测记录 CSV", initialdir=str(directory),
            filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")],
        )
        if selected:
            self.load_path(selected)
        return "break"

    def load_path(self, path):
        self.root.configure(cursor="watch")
        self.root.update_idletasks()
        try:
            self.session.load(path)
        except QueryError as exc:
            self.refresh()
            self.status_text.set(f"导入失败：{exc}")
            messagebox.showerror("导入失败", str(exc), parent=self.root)
        else:
            self.refresh()
            self.status_text.set(f"导入成功，共 {self.session.result.total} 条记录。可设置筛选条件或导出结果。")
        finally:
            self.root.configure(cursor="")

    def apply_filters(self, _event=None):
        try:
            self.session.set_filters(
                None if self.modality_text.get() == ALL else self.modality_text.get(),
                None if self.review_text.get() == ALL else self.review_text.get(),
            )
        except QueryError as exc:
            messagebox.showerror("筛选失败", str(exc), parent=self.root)
        self.refresh()
        if self.session.data is not None:
            self.status_text.set(f"筛选完成，当前 {self.session.result.total} 条记录。")

    def reset_filters(self):
        self.session.set_filters()
        self.refresh()
        if self.session.data is not None:
            self.status_text.set("已重置筛选，显示全部记录。")

    def export_file(self, _event=None):
        if self.session.data is None:
            return "break"
        directory = PROJECT_ROOT / "exports"
        selected = filedialog.asksaveasfilename(
            parent=self.root, title="导出筛选结果（请选择新文件名）",
            initialdir=str(directory), initialfile="筛选结果.csv", defaultextension=".csv",
            confirmoverwrite=False, filetypes=[("CSV 文件", "*.csv")],
        )
        if selected:
            try:
                count = self.session.export(selected)
            except QueryError as exc:
                self.status_text.set(f"导出失败：{exc}")
                messagebox.showerror("导出失败", str(exc), parent=self.root)
            else:
                self.status_text.set(f"导出成功：{count} 条记录 → {selected}")
                messagebox.showinfo("导出成功", f"已导出 {count} 条记录。\n\n{selected}", parent=self.root)
        return "break"
