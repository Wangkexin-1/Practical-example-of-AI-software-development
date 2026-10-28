import csv
import hashlib
import io
import itertools
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from record_query.core import HEADERS, QueryError, QuerySession


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "samples"


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.session = QuerySession()

    def write_input(self, text):
        path = self.directory / "input.csv"
        path.write_text(text, encoding="utf-8", newline="")
        return path

    def test_fixed_filter_answers_and_export_roundtrips(self):
        count = 0
        for name in ("original_filters.json", "all_modalities_filters.json"):
            answers = json.loads((SAMPLES / "expected" / name).read_text(encoding="utf-8"))
            source = SAMPLES / answers["source"]
            before = source.read_bytes()
            self.session.load(source)
            for case in answers["cases"]:
                with self.subTest(source=name, modality=case["modality"], status=case["review_status"]):
                    result = self.session.set_filters(case["modality"], case["review_status"])
                    self.assertEqual([row.record_id for row in result.records], case["record_ids"])
                    self.assertEqual((result.total, result.pending, result.reviewed), (case["total"], case["pending"], case["reviewed"]))
                    output = self.directory / f"result-{count}.csv"
                    self.assertEqual(self.session.export(output), result.total)
                    self.assertTrue(output.read_bytes().startswith(b"\xef\xbb\xbf"))
                    with output.open(encoding="utf-8-sig", newline="") as stream:
                        reader = csv.DictReader(stream, strict=True)
                        rows = list(reader)
                        self.assertEqual(reader.fieldnames, list(HEADERS))
                    self.assertEqual(rows, [dict(zip(HEADERS, (r.record_id, r.modality, r.review_status))) for r in result.records])
                    reloaded = QuerySession()
                    reloaded.load(output)
                    self.assertEqual(reloaded.result, result)
                    count += 1
            self.assertEqual(source.read_bytes(), before)
        self.assertEqual(count, 42)

    def test_all_invalid_fixtures_and_missing_file(self):
        manifest = json.loads((SAMPLES / "expected/manifest.json").read_text(encoding="utf-8"))
        for fixture in manifest["fixtures"]:
            if fixture["expected"] != "reject":
                continue
            with self.subTest(path=fixture["path"]):
                with self.assertRaises(QueryError) as caught:
                    self.session.load(SAMPLES / fixture["path"])
                if fixture.get("issue") == "enum":
                    self.assertIn(f"第 {fixture['line']} 行", str(caught.exception))
                    self.assertIn(fixture["column"], str(caught.exception))
                if fixture.get("issue") == "missing_column":
                    self.assertIn(fixture["column"], str(caught.exception))
                self.assertIsNone(self.session.data)
        with self.assertRaisesRegex(QueryError, "文件不存在"):
            self.session.load(SAMPLES / "invalid/does_not_exist.csv")
        with self.assertRaises(QueryError):
            self.session.load(SAMPLES)

    def test_all_valid_fixtures_and_exported_values(self):
        manifest = json.loads((SAMPLES / "expected/manifest.json").read_text(encoding="utf-8"))
        for index, fixture in enumerate(manifest["fixtures"]):
            if fixture["expected"] != "accept":
                continue
            with self.subTest(path=fixture["path"]):
                source = SAMPLES / fixture["path"]
                self.session.load(source)
                result = self.session.result
                self.assertEqual((result.total,result.pending,result.reviewed), (fixture["records"],fixture["pending"],fixture["reviewed"]))
                output = self.directory / f"valid-{index}.csv"
                self.session.export(output)
                reloaded = QuerySession()
                reloaded.load(output)
                self.assertEqual(reloaded.result, result)
                with output.open(encoding="utf-8-sig", newline="") as stream:
                    self.assertEqual(next(csv.reader(stream)), list(HEADERS))

    def test_failed_import_clears_previous_session_and_filters(self):
        self.session.load(SAMPLES / "valid/all_modalities.csv")
        self.session.set_filters("U", "待复核")
        with self.assertRaises(QueryError):
            self.session.load(SAMPLES / "invalid/invalid_modality.csv")
        self.assertIsNone(self.session.data)
        self.assertIsNone(self.session.modality)
        self.assertIsNone(self.session.review_status)
        self.assertEqual(self.session.result.total, 0)
        with self.assertRaisesRegex(QueryError, "先成功导入"):
            self.session.export(self.directory / "stale.csv")
        self.assertFalse((self.directory / "stale.csv").exists())

    def test_new_import_resets_filters(self):
        self.session.load(SAMPLES / "valid/all_modalities.csv")
        self.session.set_filters("U", "待复核")
        self.session.load(SAMPLES / "original/影像资料复核状态表.csv")
        self.assertEqual(self.session.result.total, 6)
        self.assertEqual((self.session.modality,self.session.review_status), (None,None))

    def test_invalid_filter_does_not_partially_change_conditions(self):
        self.session.load(SAMPLES / "valid/all_modalities.csv")
        expected = self.session.set_filters("U", "待复核")
        for modality,status in (("X",None), ("V","复核中"), ("u",None), ("",None)):
            with self.subTest(modality=modality,status=status):
                with self.assertRaises(QueryError):
                    self.session.set_filters(modality,status)
                self.assertEqual(self.session.result, expected)
                self.assertEqual((self.session.modality,self.session.review_status), (("U",),("待复核",)))

    def test_all_256_multi_filter_subsets(self):
        self.session.load(SAMPLES / "valid/all_modalities.csv")
        groups = {
            "U": {"S001","S002","S003","S004"},
            "V": {"S005","S006","S007"},
            "E": {"S008","S009","S010"},
            "R": {"S011","S012"},
            "C1": {"S013","S014"},
            "C2": {"S015","S016","S017","S018"},
        }
        pending = {"S001","S002","S003","S005","S008","S009","S013","S014","S015"}
        all_ids = set.union(*groups.values())
        statuses = {"待复核": pending, "已复核": all_ids - pending}
        modality_sets = [subset for n in range(7) for subset in itertools.combinations(groups,n)]
        status_sets = [subset for n in range(3) for subset in itertools.combinations(statuses,n)]
        checked = 0
        for modalities, reviews in itertools.product(modality_sets,status_sets):
            with self.subTest(modalities=modalities,reviews=reviews):
                expected_modality_ids = set.union(*(groups[m] for m in modalities)) if modalities else all_ids
                expected_status_ids = set.union(*(statuses[s] for s in reviews)) if reviews else all_ids
                expected = expected_modality_ids & expected_status_ids
                result = self.session.set_filters(modalities,reviews)
                self.assertEqual([row.record_id for row in result.records], sorted(expected))
                self.assertEqual((result.total,result.pending,result.reviewed), (len(expected),len(expected & pending),len(expected - pending)))
                checked += 1
        self.assertEqual(checked,256)

    def test_multi_filters_normalize_and_invalid_payload_is_atomic(self):
        self.session.load(SAMPLES / "valid/all_modalities.csv")
        expected = self.session.set_filters(["V","U","U"],["已复核","待复核","已复核"])
        self.assertEqual(self.session.modality,("U","V"))
        self.assertEqual(self.session.review_status,("待复核","已复核"))
        self.assertEqual(expected.total,7)
        for modality, status in ((["U","X"],None), (["E"],["待复核","非法"]), (42,None), (["U",["V"]],None)):
            with self.subTest(modality=modality,status=status):
                with self.assertRaises(QueryError):
                    self.session.set_filters(modality,status)
                self.assertEqual(self.session.result,expected)
                self.assertEqual((self.session.modality,self.session.review_status),(("U","V"),("待复核","已复核")))
        self.assertEqual(self.session.set_filters([],[]).total,18)
        self.assertIsNone(self.session.modality)
        self.assertIsNone(self.session.review_status)

    def test_multi_filter_export_matches_selection_and_preserves_source(self):
        source = SAMPLES / "valid/all_modalities.csv"
        before = source.read_bytes()
        self.session.load(source)
        self.session.set_filters(("U","V"),("待复核",))
        output = self.directory / "multi.csv"
        self.assertEqual(self.session.export(output),4)
        other = QuerySession()
        other.load(output)
        self.assertEqual([row.record_id for row in other.result.records],["S001","S002","S003","S005"])
        self.assertEqual((other.result.total,other.result.pending,other.result.reviewed),(4,4,0))
        self.assertEqual(source.read_bytes(),before)

    def test_order_duplicates_whitespace_and_quoted_newline_are_preserved(self):
        source = self.write_input('review_status,note,modality,record_id\r\n待复核,x,U,Z\r\n已复核,y,E,"ID,one"\r\n待复核,z,U,Z\r\n已复核,q,C2,"ID\r\ntwo"\r\n待复核,w,U, padded \r\n')
        self.session.load(source)
        output = self.directory / "roundtrip.csv"
        self.session.export(output)
        other = QuerySession()
        other.load(output)
        self.assertEqual(other.result, self.session.result)
        self.assertEqual([r.record_id for r in other.result.records], ["Z","ID,one","Z","ID\r\ntwo"," padded "])
        self.assertEqual([r.record_id for r in self.session.set_filters("U").records], ["Z","Z"," padded "])

    def test_duplicate_headers_bad_row_width_and_non_exact_enum_rejected(self):
        texts = [
            'record_id,modality,review_status,record_id\nA,U,待复核,B\n',
            'record_id,modality,review_status\nA,U\n',
            'record_id,modality,review_status\nA,U,待复核,extra\n',
            'record_id,modality,review_status\nA,u,待复核\n',
            'record_id,modality,review_status\nA,U, 待复核\n',
        ]
        for text in texts:
            with self.subTest(text=text), self.assertRaises(QueryError):
                self.session.load(self.write_input(text))

    def test_blank_lines_are_ignored(self):
        self.session.load(self.write_input('record_id,modality,review_status\n\nA,U,待复核\n\n'))
        self.assertEqual(self.session.result.total, 1)

    def test_input_and_equivalent_paths_cannot_be_overwritten(self):
        source = self.write_input('record_id,modality,review_status\nA,U,待复核\n')
        before = source.read_bytes()
        self.session.load(source)
        for target in (source, source.parent / "child" / ".." / source.name):
            with self.subTest(target=target), self.assertRaisesRegex(QueryError, "不得覆盖输入"):
                self.session.export(target)
        self.assertEqual(source.read_bytes(), before)

    def test_hard_link_to_source_is_protected(self):
        source = self.write_input('record_id,modality,review_status\nA,U,待复核\n')
        link = self.directory / "hardlink.csv"
        os.link(source, link)
        self.session.load(source)
        before = source.read_bytes()
        with self.assertRaisesRegex(QueryError, "不得覆盖输入"):
            self.session.export(link)
        self.assertEqual(source.read_bytes(), before)

    def test_symbolic_link_to_source_is_protected(self):
        source = self.write_input('record_id,modality,review_status\nA,U,待复核\n')
        link = self.directory / "symlink.csv"
        try:
            link.symlink_to(source)
        except OSError as exc:
            self.skipTest(f"Symbolic links unavailable: {exc}")
        self.session.load(source)
        before = source.read_bytes()
        with self.assertRaisesRegex(QueryError, "不得覆盖输入"):
            self.session.export(link)
        self.assertEqual(source.read_bytes(), before)

    def test_existing_output_is_unchanged(self):
        self.session.load(SAMPLES / "valid/single_record.csv")
        output = self.directory / "existing.csv"
        output.write_bytes(b"keep existing bytes")
        with self.assertRaisesRegex(QueryError, "已存在"):
            self.session.export(output)
        self.assertEqual(output.read_bytes(), b"keep existing bytes")

    def test_export_creation_race_and_bad_directory(self):
        self.session.load(SAMPLES / "valid/single_record.csv")
        with patch.object(Path, "open", side_effect=FileExistsError("target created by another process")):
            with self.assertRaisesRegex(QueryError, "已存在"):
                self.session.export(self.directory / "race.csv")
        with self.assertRaisesRegex(QueryError, "无法导出"):
            self.session.export(self.directory / "not-a-directory" / "out.csv")

    def test_write_failure_removes_partial_output(self):
        self.session.load(SAMPLES / "valid/single_record.csv")
        output = self.directory / "partial.csv"
        with patch("record_query.core.csv.writer") as writer:
            writer.return_value.writerows.side_effect = OSError("simulated full disk")
            with self.assertRaisesRegex(QueryError, "simulated full disk"):
                self.session.export(output)
        self.assertFalse(output.exists())
        self.assertEqual(self.session.result.total, 1)

    def test_original_sample_hashes_match_manifest_after_tests(self):
        manifest = json.loads((SAMPLES / "expected/manifest.json").read_text(encoding="utf-8"))
        for item in manifest["fixtures"]:
            self.assertEqual(hashlib.sha256((SAMPLES / item["path"]).read_bytes()).hexdigest(), item["sha256"])


if __name__ == "__main__":
    unittest.main()
