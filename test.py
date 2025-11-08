import unittest
from unittest.mock import patch, Mock
import sys
import os
import importlib
import importlib.util

MODULE_NAME = "main"
MODULE_FILE = "main.py"

def load_module_fallback():
    if os.path.exists(MODULE_FILE):
        spec = importlib.util.spec_from_file_location(MODULE_NAME, MODULE_FILE)
        module = importlib.util.module_from_spec(spec)
        sys.modules[MODULE_NAME] = module
        spec.loader.exec_module(module)
        return module
    raise ModuleNotFoundError(
        f"Module '{MODULE_NAME}' not found and '{MODULE_FILE}' does not exist in the current directory."
    )

try:
    ascii_parser = importlib.import_module(MODULE_NAME)
except ModuleNotFoundError:
    ascii_parser = load_module_fallback()

# Now import required names from the loaded module
TableParser = ascii_parser.TableParser
build_canvas_from_rows = ascii_parser.build_canvas_from_rows
fetch_html = ascii_parser.fetch_html


class TestTableParser(unittest.TestCase):
    def test_basic_table_parsing(self):
        html = """
        <table>
          <tr><td>0</td><td>█</td><td>0</td></tr>
          <tr><td>1</td><td>▀</td><td>1</td></tr>
          <tr><td>2</td><td>░</td><td>0</td></tr>
        </table>
        """
        p = TableParser()
        p.feed(html)
        self.assertEqual(len(p.rows), 3)
        self.assertIn({"x": 0, "char": "█", "y": 0}, p.rows)
        self.assertIn({"x": 1, "char": "▀", "y": 1}, p.rows)
        self.assertIn({"x": 2, "char": "░", "y": 0}, p.rows)

    def test_ignores_headers_and_malformed_rows(self):
        html = """
        <table>
          <tr><td>x</td><td>char</td><td>y</td></tr>
          <tr><td>0</td><td>A</td><td>0</td></tr>
          <tr><td>bad</td><td>B</td><td>2</td></tr>
        </table>
        """
        p = TableParser()
        p.feed(html)
        self.assertEqual(len(p.rows), 1)
        self.assertEqual(p.rows[0], {"x": 0, "char": "A", "y": 0})


class TestBuildCanvas(unittest.TestCase):
    def test_build_simple_canvas(self):
        rows = [
            {"x": 0, "char": "A", "y": 0},
            {"x": 1, "char": "B", "y": 0},
            {"x": 0, "char": "C", "y": 1},
        ]
        canvas = build_canvas_from_rows(rows)
        self.assertEqual(canvas, ["C ", "AB"])

    def test_negative_and_unordered_coords(self):
        rows = [
            {"x": -1, "char": "x", "y": -1},
            {"x": 0, "char": "y", "y": -1},
            {"x": -1, "char": "z", "y": 0},
        ]
        canvas = build_canvas_from_rows(rows)
        self.assertEqual(canvas, ["z ", "xy"])

    def test_empty_rows_returns_empty_list(self):
        self.assertEqual(build_canvas_from_rows([]), [])


class TestFetchHTML(unittest.TestCase):
    @patch(MODULE_NAME + ".requests.get")
    def test_fetch_html_success(self, mock_get):
        mock_resp = Mock()
        mock_resp.raise_for_status = Mock()
        mock_resp.text = "<html>ok</html>"
        mock_get.return_value = mock_resp

        html = fetch_html("http://example.com")
        self.assertEqual(html, "<html>ok</html>")
        mock_get.assert_called_once_with("http://example.com", timeout=10.0)

    @patch(MODULE_NAME + ".requests.get")
    def test_fetch_html_raises_exit_on_failure(self, mock_get):
        from requests import RequestException
        mock_get.side_effect = RequestException("network error")
        with self.assertRaises(SystemExit):
            fetch_html("http://bad.example")

    @patch(MODULE_NAME + ".requests.get")
    def test_fetch_html_calls_raise_for_status(self, mock_get):
        mock_resp = Mock()
        def raise_exc():
            raise Exception("bad status")
        mock_resp.raise_for_status = raise_exc
        mock_get.return_value = mock_resp
        with self.assertRaises(SystemExit):
            fetch_html("http://example.com")


if __name__ == "__main__":
    unittest.main()
