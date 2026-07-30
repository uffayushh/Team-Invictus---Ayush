"""
Primary PDF parser — PyMuPDF only, no Docker/GROBID dependency.

Produces the same shape GROBID would have (list of sections with heading +
order + text), just with heuristics instead of GROBID's trained model:

- Font size + bold-ness relative to the page's body-text size is used to
  detect headings.
- A default list of common academic section names is used as a fallback
  signal when font heuristics are ambiguous (scanned/two-column PDFs often
  have messy font metadata — see blueprint Mistake #18).

Returned shape:
    [
        {"heading": str, "section_order": int, "raw_text": str},
        ...
    ]
If no headings are detected at all (e.g. a single-column blob), the whole
document comes back as one section called "Full Text" — chunker.py handles
that case fine, it just won't have section-level citation granularity.
"""
import re
from dataclasses import dataclass

import fitz  # PyMuPDF

COMMON_HEADINGS = {
    "abstract", "introduction", "related work", "background",
    "method", "methods", "methodology", "approach",
    "experiments", "experimental setup", "results", "evaluation",
    "discussion", "limitations", "future work", "conclusion",
    "conclusions", "acknowledgments", "acknowledgements", "references",
    "appendix",
}


@dataclass
class ParsedSection:
    heading: str
    section_order: int
    raw_text: str
    page_start: int


class PdfParseError(Exception):
    pass


def parse_pdf(file_path: str, timeout_seconds: int = 30) -> list[dict]:
    """
    Parse a PDF into structured sections.

    Raises PdfParseError on failure — callers should catch this and
    surface a visible failure state (blueprint Mistake #7), not retry
    silently or hang.
    """
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        raise PdfParseError(f"Could not open PDF: {e}") from e

    if doc.page_count == 0:
        raise PdfParseError("PDF has zero pages")

    body_size = _estimate_body_font_size(doc)
    sections: list[ParsedSection] = []
    current_heading = "Preamble"
    current_text: list[str] = []
    current_page_start = 0
    order = 0

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                line_text = "".join(span["text"] for span in line["spans"]).strip()
                if not line_text:
                    continue

                if _looks_like_heading(line, line_text, body_size):
                    if current_text:
                        sections.append(ParsedSection(
                            heading=current_heading,
                            section_order=order,
                            raw_text="\n".join(current_text).strip(),
                            page_start=current_page_start,
                        ))
                        order += 1
                    current_heading = line_text
                    current_text = []
                    current_page_start = page_num
                else:
                    current_text.append(line_text)

    if current_text:
        sections.append(ParsedSection(
            heading=current_heading,
            section_order=order,
            raw_text="\n".join(current_text).strip(),
            page_start=current_page_start,
        ))

    doc.close()

    if len(sections) <= 1:
        full_text = " ".join(s.raw_text for s in sections) if sections else ""
        if not full_text.strip():
            raise PdfParseError("No extractable text found (likely a scanned PDF; OCR not implemented)")
        return [{"heading": "Full Text", "section_order": 0, "raw_text": full_text}]

    return [
        {"heading": s.heading, "section_order": s.section_order, "raw_text": s.raw_text}
        for s in sections
        if s.raw_text
    ]


def _estimate_body_font_size(doc) -> float:
    """Sample the first few pages to guess the dominant (body-text) font size."""
    sizes: dict[float, int] = {}
    for page in doc[: min(3, doc.page_count)]:
        for block in page.get_text("dict")["blocks"]:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    size = round(span["size"], 1)
                    sizes[size] = sizes.get(size, 0) + len(span["text"])
    if not sizes:
        return 10.0
    return max(sizes, key=sizes.get)


def _looks_like_heading(line: dict, text: str, body_size: float) -> bool:
    if len(text) > 80:
        return False
    normalized = re.sub(r"^\d+(\.\d+)*\.?\s*", "", text).strip().lower()
    if normalized in COMMON_HEADINGS:
        return True

    spans = line.get("spans", [])
    if not spans:
        return False
    max_size = max(s["size"] for s in spans)
    is_bold = any("bold" in s.get("font", "").lower() for s in spans)
    is_larger = max_size >= body_size + 1.5

    return len(text.split()) <= 8 and (is_bold or is_larger)