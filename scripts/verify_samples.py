"""Verify prepared fixtures and answer keys, without exercising application code."""

import csv
import hashlib
import io
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "samples"
HEADER = ["record_id", "modality", "review_status"]
MODALITIES = {"U", "V", "E", "R", "C1", "C2"}
STATUSES = {"待复核", "已复核"}


def read_csv(path):
    text = path.read_bytes().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
    rows = list(reader)
    return reader.fieldnames, rows


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    manifest = json.loads((SAMPLES / "expected/manifest.json").read_text(encoding="utf-8"))
    actual_files = {p.relative_to(SAMPLES).as_posix() for p in SAMPLES.rglob("*.csv")}
    require(actual_files == {item["path"] for item in manifest["fixtures"]}, "Fixture inventory mismatch")
    for item in manifest["fixtures"]:
        path = SAMPLES / item["path"]
        require(hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"], f"Changed bytes: {path.name}")
        issue = item.get("issue")
        if issue == "encoding":
            try:
                path.read_bytes().decode("utf-8")
            except UnicodeDecodeError:
                continue
            raise ValueError("Expected invalid UTF-8")
        if issue == "csv_syntax":
            try:
                read_csv(path)
            except csv.Error:
                continue
            raise ValueError("Expected malformed CSV")
        columns, rows = read_csv(path)
        if issue == "missing_header":
            require(columns is None and not rows, "Expected empty file")
        elif issue == "missing_column":
            require(item["column"] not in columns, "Expected missing column")
            require(set(columns) == set(HEADER) - {item["column"]}, "Unexpected missing-column fixture")
        elif issue == "enum":
            allowed = MODALITIES if item["column"] == "modality" else STATUSES
            bad_lines = [line for line, row in enumerate(rows, 2) if row[item["column"]] not in allowed]
            require(bad_lines == [item["line"]], "Unexpected invalid-enum location")
        else:
            require(all(col in columns for col in HEADER), "Missing required header")
            require(len(rows) == item["records"], "Record count mismatch")
            require(all(row["modality"] in MODALITIES and row["review_status"] in STATUSES for row in rows), "Unexpected invalid enum")
            require(sum(row["review_status"] == "待复核" for row in rows) == item["pending"], "Pending count mismatch")
            require(sum(row["review_status"] == "已复核" for row in rows) == item["reviewed"], "Reviewed count mismatch")

    checked = 0
    for name in ("all_modalities_filters.json", "original_filters.json"):
        answers = json.loads((SAMPLES / "expected" / name).read_text(encoding="utf-8"))
        _, rows = read_csv(SAMPLES / answers["source"])
        require(len(answers["cases"]) == 21, "Expected 21 combinations per answer key")
        combinations = {(case["modality"], case["review_status"]) for case in answers["cases"]}
        require(combinations == {(m, s) for m in [None, *MODALITIES] for s in [None, *STATUSES]}, "Missing filter combination")
        for case in answers["cases"]:
            selected = []
            for row in rows:
                if case["modality"] is not None and row["modality"] != case["modality"]:
                    continue
                if case["review_status"] is not None and row["review_status"] != case["review_status"]:
                    continue
                selected.append(row)
            actual = {
                "record_ids": [row["record_id"] for row in selected],
                "total": len(selected),
                "pending": sum(row["review_status"] == "待复核" for row in selected),
                "reviewed": sum(row["review_status"] == "已复核" for row in selected),
            }
            require(all(case[key] == value for key, value in actual.items()), f"Answer key mismatch: {name}, {case}")
            checked += 1
    require(read_csv(SAMPLES / "valid/all_modalities.csv") == read_csv(SAMPLES / "valid/all_modalities_bom.csv"), "BOM content mismatch")
    require(not (SAMPLES / "invalid/does_not_exist.csv").exists(), "Missing-file scenario must remain absent")
    print(f"Fixture checks passed: {len(actual_files)} CSV files; {checked} expected filter combinations.")
    print("This checks preparation data only. Application acceptance: NOT_RUN.")


if __name__ == "__main__":
    main()
