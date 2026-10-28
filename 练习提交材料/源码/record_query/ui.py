"""Tkinter view and user event endpoints (FU-UI-0001)."""

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .core import HEADERS, MODALITIES, REVIEW_STATUSES, QueryError, QuerySession


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ALL = "全部"
UNSELECTED = "请选择"


class FilterGroup(ttk.LabelFrame):
    """Dynamic input rows; selected values are submitted to the session as payload."""

    def __init__(self, parent, title, choices, on_change):
        super().__init__(parent, text=title, padding=8)
        self.choices = tuple(choices)
        self.on_change = on_change
        self.rows = []
        self.columnconfigure(0, weight=1)
        self.rows_frame = ttk.Frame(self)
        self.rows_frame.grid(row=0, column=0, sticky="ew")
        self.add_button = ttk.Button(self, text="+ 增加条件", command=self.add_row)
        self.add_button.grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.sync(None, reset=True)

    def selected_values(self):
        return tuple(row["variable"].get() for row in self.rows if row["variable"].get() in self.choices)

    def _append_row(self, value):
        frame = ttk.Frame(self.rows_frame)
        frame.columnconfigure(0, weight=1)
        variable = tk.StringVar(master=self, value=value)
        combo = ttk.Combobox(frame, textvariable=variable, state="readonly", width=14)
        combo.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        row = {"frame": frame, "variable": variable, "combo": combo}
        remove = ttk.Button(frame, text="移除", width=5, command=lambda: self.remove_row(row))
        remove.grid(row=0, column=1)
        row["remove"] = remove
        combo.bind("<<ComboboxSelected>>", lambda event: self._changed(row))
        self.rows.append(row)
        return row

    def _update_options(self):
        placeholder = ALL if len(self.rows) == 1 else UNSELECTED
        for index, row in enumerate(self.rows):
            row["frame"].grid(row=index, column=0, sticky="ew", pady=(0, 4))
            if row["variable"].get() in (ALL, UNSELECTED):
                row["variable"].set(placeholder)
            others = {other["variable"].get() for other in self.rows if other is not row}
            row["combo"].configure(values=(placeholder, *(value for value in self.choices if value not in others)))
            row["remove"].configure(state="normal" if len(self.rows) > 1 else "disabled")
        self.add_button.configure(state="normal" if len(self.rows) < len(self.choices) else "disabled")
        self.rows_frame.columnconfigure(0, weight=1)

    def _changed(self, row):
        others = {other["variable"].get() for other in self.rows if other is not row}
        if row["variable"].get() in others and row["variable"].get() in self.choices:
            row["variable"].set(UNSELECTED)
        self._update_options()
        self.on_change()

    def add_row(self):
        if len(self.rows) >= len(self.choices):
            return
        row = self._append_row(UNSELECTED)
        self._update_options()
        row["combo"].focus_set()

    def remove_row(self, row):
        if len(self.rows) <= 1:
            return
        self.rows.remove(row)
        row["frame"].destroy()
        self._update_options()
        self.on_change()

    def sync(self, values, reset=False):
        values = tuple(values or ())
        if reset or set(self.selected_values()) != set(values):
            for row in self.rows:
                row["frame"].destroy()
            self.rows.clear()
            for value in values or (ALL,):
                self._append_row(value)
        self._update_options()


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
        self.total_text = tk.StringVar()
        self.pending_text = tk.StringVar()
        self.reviewed_text = tk.StringVar()
        self.status_text = tk.StringVar(value="请选择 UTF-8 CSV 文件开始查询。")

        frame = ttk.Frame(root, padding=18)
        self.content_frame = frame
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
        filters.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        filters.columnconfigure(0, weight=1)
        filters.columnconfigure(1, weight=1)
        self.modality_group = FilterGroup(filters, "modality（可多选）", MODALITIES, self.apply_filters)
        self.modality_group.grid(row=0, column=0, sticky="new", padx=(0, 12))
        self.review_group = FilterGroup(filters, "review_status（可多选）", REVIEW_STATUSES, self.apply_filters)
        self.review_group.grid(row=0, column=1, sticky="new", padx=(0, 12))
        self.reset_button = ttk.Button(filters, text="重置筛选", command=self.reset_filters)
        self.reset_button.grid(row=0, column=2, sticky="n", pady=8)
        ttk.Label(filters, text="同一项内任意匹配，两项之间同时满足。").grid(
            row=1, column=0, columnspan=3, sticky="w", pady=(6, 0)
        )

        counts = ttk.Frame(frame)
        counts.grid(row=3, column=0, sticky="ew", pady=(0, 12))
        for index, variable in enumerate((self.total_text, self.pending_text, self.reviewed_text)):
            ttk.Label(counts, textvariable=variable, style="Count.TLabel").grid(
                row=0, column=index, sticky="w", padx=(0, 45)
            )

        table = ttk.Frame(frame)
        self.table_frame = table
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
        filters.bind("<Configure>", self._fit_filter_rows)
        root.after_idle(self._fit_filter_rows)
        self.import_button.focus_set()

    def _fit_filter_rows(self, _event=None):
        minimum = self.content_frame.winfo_reqheight() - self.table_frame.winfo_reqheight() + 110
        self.root.minsize(740, max(460, minimum))

    @property
    def modality_combo(self):
        return self.modality_group.rows[0]["combo"]

    @property
    def review_combo(self):
        return self.review_group.rows[0]["combo"]

    @property
    def modality_text(self):
        return self.modality_group.rows[0]["variable"]

    @property
    def review_text(self):
        return self.review_group.rows[0]["variable"]

    def refresh(self, reset_filter_rows=False):
        data = self.session.data
        result = self.session.result
        self.path_text.set(str(data.source_path) if data else "尚未导入文件")
        self.modality_group.sync(self.session.modality, reset=reset_filter_rows)
        self.review_group.sync(self.session.review_status, reset=reset_filter_rows)
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
            self.refresh(reset_filter_rows=True)
            self.status_text.set(f"导入失败：{exc}")
            messagebox.showerror("导入失败", str(exc), parent=self.root)
        else:
            self.refresh(reset_filter_rows=True)
            self.status_text.set(f"导入成功，共 {self.session.result.total} 条记录。可设置筛选条件或导出结果。")
        finally:
            self.root.configure(cursor="")

    def apply_filters(self, _event=None):
        try:
            self.session.set_filters(
                self.modality_group.selected_values(),
                self.review_group.selected_values(),
            )
        except QueryError as exc:
            messagebox.showerror("筛选失败", str(exc), parent=self.root)
        self.refresh()
        if self.session.data is not None:
            self.status_text.set(f"筛选完成，当前 {self.session.result.total} 条记录。")

    def reset_filters(self):
        self.session.set_filters()
        self.refresh(reset_filter_rows=True)
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
