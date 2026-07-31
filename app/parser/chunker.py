"""
Section-aware + recursive chunker.

Target chunk size sits deliberately between the two failure modes called
out in the blueprint (Mistakes #9 and #10):
  - too small (~100 tokens) -> citations read as meaningless slivers
  - too large (~2000 tokens) -> a citation "points to half a page"

~300-500 tokens (roughly 1200-2000 characters) per chunk, with overlap so
claims near a chunk boundary don't lose context.
"""
from dataclasses import dataclass

TARGET_CHARS = 1500
OVERLAP_CHARS = 200
MIN_CHARS = 200  # don't emit a trailing chunk this small; merge it back


@dataclass
class ChunkResult:
    section_heading: str
    section_order: int
    chunk_index: int
    text: str


def chunk_sections(sections: list[dict]) -> list[ChunkResult]:
    """
    sections: [{"heading", "section_order", "raw_text"}, ...] as returned
    by pymupdf_parser.parse_pdf or grobid_client.parse_pdf.
    """
    chunks: list[ChunkResult] = []
    global_index = 0

    for section in sections:
        text = section["raw_text"]
        if not text.strip():
            continue

        pieces = _recursive_split(text)
        for piece in pieces:
            chunks.append(ChunkResult(
                section_heading=section["heading"],
                section_order=section["section_order"],
                chunk_index=global_index,
                text=piece,
            ))
            global_index += 1

    return chunks


def _recursive_split(text: str) -> list[str]:
    """Split on paragraph boundaries first, then sentences, packing
    greedily up to TARGET_CHARS with OVERLAP_CHARS carried into the next
    chunk."""
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    if not paragraphs:
        return []

    pieces: list[str] = []
    current = ""

    for para in paragraphs:
        candidate = f"{current}\n{para}".strip() if current else para

        if len(candidate) <= TARGET_CHARS:
            current = candidate
            continue

        if current:
            pieces.append(current)
        if len(para) <= TARGET_CHARS:
            current = para
        else:
            sub_pieces, leftover = _split_long_paragraph(para)
            pieces.extend(sub_pieces)
            current = leftover

    if current:
        if pieces and len(current) < MIN_CHARS:
            pieces[-1] = f"{pieces[-1]} {current}".strip()
        else:
            pieces.append(current)

    return _apply_overlap(pieces)


def _split_long_paragraph(para: str) -> tuple[list[str], str]:
    sentences = [s.strip() for s in para.replace("? ", "?|").replace("! ", "!|")
                 .replace(". ", ".|").split("|") if s.strip()]
    pieces = []
    current = ""
    for sent in sentences:
        candidate = f"{current} {sent}".strip()
        if len(candidate) <= TARGET_CHARS:
            current = candidate
        else:
            if current:
                pieces.append(current)
            current = sent
    return pieces, current


def _apply_overlap(pieces: list[str]) -> list[str]:
    if len(pieces) <= 1:
        return pieces
    overlapped = [pieces[0]]
    for i in range(1, len(pieces)):
        prev_tail = pieces[i - 1][-OVERLAP_CHARS:]
        overlapped.append(f"{prev_tail} {pieces[i]}".strip())
    return overlapped