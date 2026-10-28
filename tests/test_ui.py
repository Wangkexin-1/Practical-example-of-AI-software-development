"""Automated Tk widget integration; distinct from native keyboard/mouse checks."""

from pathlib import Path
import tempfile
import tkinter as tk
import unittest
from unittest.mock import patch

from record_query.ui import ALL, QueryWindow


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
