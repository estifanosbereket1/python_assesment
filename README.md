# ASCII Art Parser

This project parses an HTML table containing `x`, `char`, and `y` columns, and converts it into ASCII art printed in the terminal.

---

## Overview

The program fetches a web page, extracts table data, and maps characters to coordinates on a grid to form ASCII art.

---

## Libraries and Modules Used

1. **`html.parser.HTMLParser`**  
   Used for parsing HTML and extracting data from `<table>` rows.

2. **`requests`**  
   Handles HTTP requests to fetch the web page content.

3. **`argparse`**  
   Manages command-line arguments like the input URL.

4. **`unittest` and `unittest.mock`**  
   Used for automated testing, including mocking network requests.

---

## Main Components

### **1. TableParser class**
- Inherits from `HTMLParser`.  
- Detects `<tr>` and `<td>` elements.  
- Collects data for each table row.  
- When a row has three valid cells (`x`, `char`, `y`), it adds it to the `rows` list.

### **2. fetch_html(url)**
- Downloads the given web page.
- Handles network errors and invalid responses.
- Exits gracefully if a problem occurs.

### **3. build_canvas_from_rows(rows)**
- Calculates the canvas boundaries from all x/y coordinates.
- Creates a text grid (filled with spaces).
- Places each character on its corresponding (x, y) position.
- Returns a list of strings representing the ASCII art.

### **4. main()**
- Reads the `-url` command-line argument.
- Fetches and parses the HTML using `TableParser`.
- Builds and prints the ASCII art to the terminal.

---

## Main File
**Main function** * Reads the -url * Fetches the HTML. * Parses it with TableParser a custom class which inherits from HTMLParsre and overides the three methods. * Builds and prints the ASCII art. 
--- 

## Example 

### Linux based Os(mine)
bash
python3 main.py -url "https://example.com/ascii_table.html"

### Windows
bash
python main.py -url "https://example.com/ascii_table

---

## Running Tests

Tests are included in **`test.py`** and cover:
- Table parsing behavior  
- Canvas building logic  
- Network fetching and error handling  

### Run all tests
```bash
python3 -m unittest test.py
