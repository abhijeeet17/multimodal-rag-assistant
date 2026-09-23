import re
from typing import List, Optional
import pandas as pd


def extract_tables_from_pdf_page(page_obj: any) -> List[str]:
    """
    Detect tables on a PyMuPDF PDF page using page.find_tables().
    Converts tables into clean pipe-delimited text representations.
    """
    formatted_tables = []
    try:
        tabs = page_obj.find_tables()
        for tab in tabs:
            df = tab.to_pandas()
            if not df.empty:
                # Format dataframe as markdown table string
                markdown_table = df.to_markdown(index=False)
                formatted_tables.append(markdown_table)
    except Exception:
        pass
    return formatted_tables


def format_table_to_structured_text(headers: List[str], rows: List[List[str]]) -> str:
    """Format custom headers and rows into structured pipe text."""
    if not headers or not rows:
        return ""

    header_str = " | ".join(headers)
    divider = " | ".join(["---"] * len(headers))
    row_strs = [" | ".join(row) for row in rows]

    return f"{header_str}\n{divider}\n" + "\n".join(row_strs)
