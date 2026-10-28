"""CSV contracts and the authoritative query session (AV-0001)."""

import csv
from dataclasses import dataclass
import os
from pathlib import Path


HEADERS = ("record_id", "modality", "review_status")
MODALITIES = ("U", "V", "E", "R", "C1", "C2")
REVIEW_STATUSES = ("待复核", "已复核")


class QueryError(Exception):
    """An actionable validation or file-operation error."""


@dataclass(frozen=True)
class Record:
    record_id: str
    modality: str
    review_status: str


@dataclass(frozen=True)
class LoadedData:
    source_path: Path
    source_identity: tuple[int, int]
    records: tuple[Record, ...]


@dataclass(frozen=True)
class Result:
    records: tuple[Record, ...]
    total: int
    pending: int
    reviewed: int


def _identity(stat_result):
    return stat_result.st_dev, stat_result.st_ino


def read_records(file_path):
    """FU-0001: validate the entire source before returning immutable data."""
    path = Path(file_path)
    reader = None
    try:
        path = path.resolve()
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            source_identity = _identity(os.fstat(stream.fileno()))
            reader = csv.reader(stream, strict=True)
            columns = next(reader, None)
            if not columns:
                raise QueryError("缺少表头：必须包含 record_id、modality、review_status 三列。")
            missing = [name for name in HEADERS if name not in columns]
            if missing:
                raise QueryError("缺少必需列：" + "、".join(missing) + "。")
            if len(set(columns)) != len(columns):
                raise QueryError("表头含重复列名，请为每列使用不同名称。")
            positions = [columns.index(name) for name in HEADERS]
            records = []
            for row in reader:
                if not row:
                    continue
                line = reader.line_num
                if len(row) != len(columns):
                    raise QueryError(
                        f"第 {line} 行字段数错误：应为 {len(columns)} 列，实际 {len(row)} 列。"
                    )
                record = Record(*(row[index] for index in positions))
                if record.modality not in MODALITIES:
                    raise QueryError(
                        f"第 {line} 行 modality 值 {record.modality!r} 非法；"
                        "仅允许 U、V、E、R、C1、C2。"
                    )
                if record.review_status not in REVIEW_STATUSES:
                    raise QueryError(
                        f"第 {line} 行 review_status 值 {record.review_status!r} 非法；"
                        "仅允许待复核、已复核。"
                    )
                records.append(record)
        return LoadedData(path, source_identity, tuple(records))
    except FileNotFoundError as exc:
        raise QueryError(f"文件不存在：{path}") from exc
    except UnicodeDecodeError as exc:
        raise QueryError(f"文件不是有效的 UTF-8 编码，请使用 UTF-8 保存：{path}") from exc
    except csv.Error as exc:
        line = reader.line_num if reader is not None else 1
        raise QueryError(f"CSV 格式错误，位于第 {line} 行附近：{exc}") from exc
    except (OSError, ValueError, RuntimeError) as exc:
        raise QueryError(f"无法读取文件 {path}：{exc}") from exc


class QuerySession:
    """AV-0001: only owner of imported data and active query conditions."""

    def __init__(self):
        self.data = None
        self.modality = None
        self.review_status = None

    def clear(self):
        self.data = None
        self.modality = None
        self.review_status = None

    def load(self, file_path):
        self.clear()
        self.data = read_records(file_path)
        return self.result

    def set_filters(self, modality=None, review_status=None):
        """FU-0002: reject invalid payloads before changing either condition."""
        if modality is not None and modality not in MODALITIES:
            raise QueryError(f"筛选 modality 值非法：{modality!r}。")
        if review_status is not None and review_status not in REVIEW_STATUSES:
            raise QueryError(f"筛选 review_status 值非法：{review_status!r}。")
        self.modality = modality
        self.review_status = review_status
        return self.result

    @property
    def result(self):
        records = () if self.data is None else tuple(
            row for row in self.data.records
            if (self.modality is None or row.modality == self.modality)
            and (self.review_status is None or row.review_status == self.review_status)
        )
        pending = sum(row.review_status == "待复核" for row in records)
        return Result(records, len(records), pending, len(records) - pending)

    def export(self, file_path):
        """FU-0003: create a new CSV exclusively; never truncate an existing file."""
        if self.data is None:
            raise QueryError("请先成功导入 CSV 文件，再导出结果。")
        target = Path(file_path)
        created_identity = None
        result = self.result
        try:
            target = target.resolve()
            source = self.data.source_path
            if os.path.normcase(str(target)) == os.path.normcase(str(source)):
                raise QueryError("不得覆盖输入文件，请选择新的文件名或目录。")
            try:
                existing_identity = _identity(target.stat())
            except FileNotFoundError:
                existing_identity = None
            if existing_identity is not None:
                if existing_identity == self.data.source_identity or (
                    source.exists() and os.path.samefile(target, source)
                ):
                    raise QueryError("目标与输入文件指向同一文件，不得覆盖输入文件。")
                raise QueryError("目标文件已存在，请使用新的文件名；已有文件不会被覆盖。")
            with target.open("x", encoding="utf-8-sig", newline="") as stream:
                created_identity = _identity(os.fstat(stream.fileno()))
                writer = csv.writer(stream)
                writer.writerow(HEADERS)
                writer.writerows(
                    (row.record_id, row.modality, row.review_status)
                    for row in result.records
                )
            return result.total
        except (OSError, ValueError, RuntimeError, csv.Error) as exc:
            if created_identity is not None:
                try:
                    if _identity(target.stat()) == created_identity:
                        target.unlink()
                except OSError:
                    raise QueryError(
                        f"导出失败：{exc}。不完整文件未能清理，请检查：{target}"
                    ) from exc
            if isinstance(exc, FileExistsError):
                raise QueryError("目标文件已存在，请使用新的文件名；已有文件不会被覆盖。") from exc
            raise QueryError(f"无法导出到 {target}：{exc}") from exc
