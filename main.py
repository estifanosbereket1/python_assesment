from html.parser import HTMLParser
import requests
import argparse
import sys
from typing import List, Dict


class TableParser(HTMLParser):
    """
    Parses an HTML table containing x, character, and y coordinates.

    Builds a list of dictionaries like:
    [{"x": 0, "char": "█", "y": 0}, {"x": 1, "char": "▀", "y": 2}, ...]
    """

    def __init__(self):
        super().__init__()
        self.in_td = False        
        self.current_row = []    
        self.rows = []            
        self.data_buffer = ""  

    # Overriding default HTMLParser methods
    def handle_starttag(self, tag, attrs):
        if tag == "td":
            self.in_td = True
            self.data_buffer = ""  
        elif tag == "tr":
            self.current_row = [] 

    def handle_data(self, data):
        if self.in_td:
            clean_data = data.strip()
            if clean_data:
                self.data_buffer += clean_data  

    def handle_endtag(self, tag):
        if tag == "td":
            self.in_td = False
            self.current_row.append(self.data_buffer)
        elif tag == "tr":
            if len(self.current_row) == 3:
                try:
                    x = int(self.current_row[0])
                    char = self.current_row[1]
                    y = int(self.current_row[2])
                    self.rows.append({"x": x, "char": char, "y": y})
                except ValueError:
                    # Skip invalid rows or headers
                    pass
"""
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments containing the URL.
 """

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="ASCII Art Parser")
    p.add_argument("-url", required=True, help="URL of the ASCII Art")
    return p.parse_args()


def fetch_html(url: str, timeout: float = 10.0) -> str:
    """
    Fetch HTML content from a URL.

    Args:
        url (str): The URL to fetch.
        timeout (float): Request timeout in seconds.

    Returns:
        str: HTML response text.

    Exits the program on any request/HTTP-related error.
    """
    try:
        resp = requests.get(url, timeout=timeout)
       
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as exc:
        print(f"Error fetching URL '{url}': {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Unexpected error fetching URL '{url}': {exc}", file=sys.stderr)
        sys.exit(1)



def build_canvas_from_rows(rows: List[Dict[str, object]]) -> List[str]:
    """
    Convert parsed coordinate rows into an ASCII art canvas.

    Steps:
      1. Find min/max x and y to calculate canvas size.
      2. Create an empty 2D list.
      3. Map each (x, y) coordinate to a position in the list.
      4. Convert the 2D list into printable strings.

    Args:
        rows (List[Dict[str, object]]): Parsed coordinate data.

    Returns:
        List[str]: Lines of ASCII art.
    """
    if not rows:
        return []

    xs = [r["x"] for r in rows]
    ys = [r["y"] for r in rows]

    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)

    width = x_max - x_min + 1
    height = y_max - y_min + 1

    canvas = [[" " for _ in range(width)] for _ in range(height)]

    for r in rows:
        x = r["x"]
        y = r["y"]
        ch = r["char"]

        col = x - x_min
        row_from_bottom = y - y_min
        canvas_row = height - 1 - row_from_bottom
        canvas[canvas_row][col] = ch

    return ["".join(line) for line in canvas]


def main() -> None:
    """
    Main entry point.
    Fetches HTML, parses the table, builds ASCII art, and prints it.
    """
    args = parse_args()
    html = fetch_html(args.url)

    parser = TableParser()
    parser.feed(html)

    if not parser.rows:
        print("No valid rows found in the table.", file=sys.stderr)
        sys.exit(1)

    canvas_lines = build_canvas_from_rows(parser.rows)

    for line in canvas_lines:
        print(line)


if __name__ == "__main__":
    main()
