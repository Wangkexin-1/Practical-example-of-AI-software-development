"""Automated Tk widget integration; distinct from native keyboard/mouse checks."""

from pathlib import Path
import tempfile
import tkinter as tk
import unittest
from unittest.mock import patch

from record_query.core import MODALITIES, QuerySession
from record_query.ui import ALL, UNSELECTED, QueryWindow


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "samples/original/影像资料复核状态表.csv"


class UITests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = QueryWindow(self.root)
        self.root.update()

    def tearDown(self):
        self.root.destroy()

    def select(self, group, index, value):
        combo = group.rows[index]["combo"]
        self.assertIn(value, combo["values"])
        combo.set(value)
        combo.event_generate("<<ComboboxSelected>>")
        self.root.update()

    def test_dynamic_multi_groups_filter_statistics_and_export(self):
        self.app.load_path(ROOT / "samples/valid/all_modalities.csv")
        modality = self.app.modality_group
        review = self.app.review_group
        self.select(modality,0,"U")
        modality.add_button.invoke()
        self.assertEqual(modality.rows[1]["variable"].get(),UNSELECTED)
        self.assertNotIn("U",modality.rows[1]["combo"]["values"])
        self.select(modality,1,"V")
        self.assertEqual(len(self.app.tree.get_children()),7)
        self.select(review,0,"待复核")
        self.assertEqual((self.app.total_text.get(),self.app.pending_text.get(),self.app.reviewed_text.get()),("总数：4","待复核：4","已复核：0"))
        review.add_button.invoke()
        self.assertNotIn("待复核",review.rows[1]["combo"]["values"])
        self.select(review,1,"已复核")
        self.assertEqual(len(self.app.tree.get_children()),7)
        self.assertEqual(str(review.add_button["state"]),"disabled")
        self.assertEqual(self.app.session.review_status,("待复核","已复核"))
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "multi.csv"
            with patch("record_query.ui.filedialog.asksaveasfilename",return_value=str(output)), patch("record_query.ui.messagebox.showinfo"):
                self.app.export_button.invoke()
            other = QuerySession()
            other.load(output)
            self.assertEqual([row.record_id for row in other.result.records],[f"S{i:03}" for i in range(1,8)])

    def test_dynamic_options_reclaimed_after_change_and_remove(self):
        self.app.load_path(SAMPLE)
        group = self.app.modality_group
        self.select(group,0,"U")
        group.add_button.invoke()
        self.select(group,1,"V")
        self.assertNotIn("V",group.rows[0]["combo"]["values"])
        self.select(group,0,"E")
        self.assertIn("U",group.rows[1]["combo"]["values"])
        self.assertNotIn("E",group.rows[1]["combo"]["values"])
        group.rows[0]["remove"].invoke()
        self.assertEqual(group.selected_values(),("V",))
        self.assertIn("E",group.rows[0]["combo"]["values"])
        self.assertEqual(self.app.session.result.total,1)
        self.assertEqual(str(group.rows[0]["remove"]["state"]),"disabled")

    def test_blank_additions_do_not_select_implicitly_and_reset_clears_rows(self):
        self.app.load_path(SAMPLE)
        group = self.app.modality_group
        group.add_button.invoke()
        self.assertEqual([row["variable"].get() for row in group.rows],[UNSELECTED,UNSELECTED])
        self.assertEqual(self.app.session.result.total,6)
        self.select(group,1,"U")
        group.add_button.invoke()
        self.assertEqual(self.app.session.result.total,2)
        self.assertNotIn("U",group.rows[0]["combo"]["values"])
        group.rows[1]["remove"].invoke()
        self.assertEqual(self.app.session.result.total,6)
        self.assertEqual(len(group.rows),2)
        self.app.review_group.add_button.invoke()
        self.app.reset_button.invoke()
        for target in (self.app.modality_group,self.app.review_group):
            self.assertEqual(len(target.rows),1)
            self.assertEqual(target.rows[0]["variable"].get(),ALL)

    def test_all_distinct_choices_limit_and_removal_enable_add_again(self):
        group = self.app.modality_group
        for index,value in enumerate(MODALITIES):
            if index:
                group.add_button.invoke()
            self.select(group,index,value)
        self.assertEqual(len(group.rows),6)
        self.assertEqual(str(group.add_button["state"]),"disabled")
        for row in group.rows:
            self.assertEqual(tuple(row["combo"]["values"]),(UNSELECTED,row["variable"].get()))
        group.rows[-1]["remove"].invoke()
        self.assertEqual(str(group.add_button["state"]),"normal")
        self.assertIn("C2",group.rows[0]["combo"]["values"])
        group.add_button.invoke()
        self.assertEqual(tuple(group.rows[-1]["combo"]["values"]),(UNSELECTED,"C2"))

    def test_reimport_and_failure_reset_multi_rows_cancel_preserves_drafts(self):
        self.app.load_path(SAMPLE)
        self.select(self.app.modality_group,0,"U")
        self.app.modality_group.add_button.invoke()
        self.select(self.app.modality_group,1,"V")
        self.app.review_group.add_button.invoke()
        with patch("record_query.ui.filedialog.askopenfilename",return_value=""):
            self.app.open_file()
        self.assertEqual(len(self.app.modality_group.rows),2)
        self.assertEqual(len(self.app.review_group.rows),2)
        self.assertEqual(self.app.session.modality,("U","V"))
        self.app.load_path(SAMPLE)
        self.assertEqual(len(self.app.modality_group.rows),1)
        self.assertEqual(self.app.modality_text.get(),ALL)
        self.app.modality_group.add_button.invoke()
        self.app.review_group.add_button.invoke()
        with patch("record_query.ui.messagebox.showerror"):
            self.app.load_path(ROOT / "samples/invalid/invalid_modality.csv")
        self.assertEqual(len(self.app.modality_group.rows),1)
        self.assertEqual(len(self.app.review_group.rows),1)
        self.assertEqual(self.app.session.result.total,0)
        self.assertEqual(str(self.app.export_button["state"]),"disabled")

    def test_maximum_filter_rows_keep_table_and_export_visible(self):
        for _ in range(5):
            self.app.modality_group.add_button.invoke()
        self.app.review_group.add_button.invoke()
        self.root.deiconify()
        self.root.geometry("740x460")
        self.root.update()
        bottom = self.app.export_button.winfo_rooty() - self.root.winfo_rooty() + self.app.export_button.winfo_height()
        self.assertLessEqual(bottom,self.root.winfo_height())
        self.assertGreaterEqual(self.app.tree.winfo_height(),80)

    def test_empty_then_import_filter_reset_and_export(self):
        self.assertEqual(str(self.app.export_button["state"]), "disabled")
        with patch("record_query.ui.filedialog.askopenfilename", return_value=str(SAMPLE)):
            self.app.import_button.invoke()
        self.assertEqual(len(self.app.tree.get_children()), 6)
        self.assertEqual((self.app.total_text.get(),self.app.pending_text.get(),self.app.reviewed_text.get()), ("总数：6","待复核：3","已复核：3"))
        self.app.modality_combo.set("U")
        self.app.modality_combo.event_generate("<<ComboboxSelected>>")
        self.app.review_combo.set("待复核")
        self.app.review_combo.event_generate("<<ComboboxSelected>>")
        self.root.update()
        self.assertEqual(len(self.app.tree.get_children()), 1)
        first = self.app.tree.get_children()[0]
        self.assertEqual(self.app.tree.item(first,"values"), ("R001","U","待复核"))
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "filtered.csv"
            with patch("record_query.ui.filedialog.asksaveasfilename", return_value=str(output)), patch("record_query.ui.messagebox.showinfo") as info:
                self.app.export_button.invoke()
            self.assertTrue(output.is_file())
            info.assert_called_once()
        self.app.reset_button.invoke()
        self.assertEqual(self.app.modality_text.get(), ALL)
        self.assertEqual(self.app.review_text.get(), ALL)
        self.assertEqual(len(self.app.tree.get_children()), 6)

    def test_import_and_export_cancel_leave_query_unchanged(self):
        self.app.load_path(SAMPLE)
        expected = self.app.session.data
        with patch("record_query.ui.filedialog.askopenfilename", return_value=""):
            self.app.open_file()
        with patch("record_query.ui.filedialog.asksaveasfilename", return_value=""), patch.object(self.app.session,"export") as export:
            self.app.export_file()
            export.assert_not_called()
        self.assertIs(self.app.session.data, expected)
        self.assertEqual(len(self.app.tree.get_children()), 6)

    def test_failed_import_clears_table_and_disables_export(self):
        self.app.load_path(SAMPLE)
        with patch("record_query.ui.messagebox.showerror") as error:
            self.app.load_path(ROOT / "samples/invalid/invalid_modality.csv")
        error.assert_called_once()
        self.assertIn("第 3 行", error.call_args.args[1])
        self.assertEqual(len(self.app.tree.get_children()), 0)
        self.assertEqual(self.app.total_text.get(), "总数：0")
        self.assertEqual(str(self.app.export_button["state"]), "disabled")

    def test_empty_valid_input_enables_export_and_export_error_keeps_state(self):
        self.app.load_path(ROOT / "samples/valid/header_only.csv")
        self.assertEqual(str(self.app.export_button["state"]), "normal")
        with patch("record_query.ui.filedialog.asksaveasfilename", return_value=str(ROOT / "samples/valid/header_only.csv")), patch("record_query.ui.messagebox.showerror") as error:
            self.app.export_file()
        error.assert_called_once()
        self.assertIsNotNone(self.app.session.data)
        self.assertIn("不得覆盖输入", error.call_args.args[1])


if __name__ == "__main__":
    unittest.main()
