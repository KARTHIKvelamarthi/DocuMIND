# backend/ingestion/visual_extractor.py
# Extracts images and tables from a PDF and attaches them to chunks by page.
# Does NOT modify chunking logic — only extends chunk metadata.

import os
from typing import List, Dict

import fitz          # PyMuPDF
import pdfplumber


ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "images")

# Images smaller than this (in either dimension) are treated as icons and skipped
MIN_IMAGE_PX = 60

# Header/footer zone: images whose top edge is within this many points of the
# page top, or whose bottom edge is within this many points of the page bottom,
# are considered decorative and skipped.
HEADER_FOOTER_MARGIN = 80


# ---------------------------------------------------------------------------
# Image extraction  (header/footer + tiny-image filtering)
# ---------------------------------------------------------------------------

def extract_images(file_path: str, assets_dir: str = ASSETS_DIR) -> List[Dict]:
    """
    Extract content images from a PDF using PyMuPDF.
    Skips images located in the header/footer zone and very small icons.

    Returns:
        List of { "page": int, "path": str }
    """
    os.makedirs(assets_dir, exist_ok=True)
    results = []
    skipped = 0

    doc = fitz.open(file_path)
    pdf_name = os.path.splitext(os.path.basename(file_path))[0]

    for page_num in range(len(doc)):
        page       = doc[page_num]
        page_h     = page.rect.height
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            xref = img[0]

            # ── Position filter ──────────────────────────────────────────────
            try:
                rects = page.get_image_rects(xref)
            except Exception:
                rects = []

            in_header_footer = False
            if rects:
                bbox = rects[0]          # fitz.Rect
                y_top    = bbox.y0
                y_bottom = bbox.y1
                width    = bbox.width
                height   = bbox.height

                # Skip header/footer zone
                if y_top < HEADER_FOOTER_MARGIN or y_bottom > page_h - HEADER_FOOTER_MARGIN:
                    in_header_footer = True

                # Skip tiny icons
                if width < MIN_IMAGE_PX or height < MIN_IMAGE_PX:
                    in_header_footer = True

            if in_header_footer:
                skipped += 1
                continue

            # ── Extract & save ───────────────────────────────────────────────
            try:
                base_image   = doc.extract_image(xref)
                image_bytes  = base_image["image"]
                ext          = base_image["ext"]
            except Exception:
                continue

            filename  = f"{pdf_name}_p{page_num + 1}_img{img_index + 1}.{ext}"
            save_path = os.path.join(assets_dir, filename)

            with open(save_path, "wb") as f:
                f.write(image_bytes)

            results.append({"page": page_num + 1, "path": save_path})

    doc.close()
    print(f"   Extracted {len(results)} images ({skipped} header/footer/icon skipped) "
          f"from '{os.path.basename(file_path)}'")
    return results


# ---------------------------------------------------------------------------
# Table extraction
# ---------------------------------------------------------------------------

def extract_tables(file_path: str) -> List[Dict]:
    """
    Extract all tables from a PDF using pdfplumber.

    Returns:
        List of { "page": int, "data": List[List] }
    """
    results = []

    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table in tables:
                if table:
                    results.append({
                        "page": page_num + 1,
                        "data": table,
                    })

    print(f"   Extracted {len(results)} tables from '{os.path.basename(file_path)}'")
    return results


# ---------------------------------------------------------------------------
# Attach visuals to chunks by page number
# ---------------------------------------------------------------------------

def attach_visuals_to_chunks(chunks: List[Dict], images: List[Dict], tables: List[Dict]) -> List[Dict]:
    """
    Attach image and table metadata to each chunk based on matching page number.
    Mutates chunks in-place and returns them.
    """
    # Build page-keyed lookup maps
    images_by_page: Dict[int, List[Dict]] = {}
    for img in images:
        images_by_page.setdefault(img["page"], []).append(img)

    tables_by_page: Dict[int, List[Dict]] = {}
    for tbl in tables:
        tables_by_page.setdefault(tbl["page"], []).append(tbl)

    for chunk in chunks:
        page = chunk.get("page", -1)
        chunk["images"] = images_by_page.get(page, [])
        chunk["tables"] = tables_by_page.get(page, [])

    return chunks


# ---------------------------------------------------------------------------
# Convenience: run full visual extraction and attach in one call
# ---------------------------------------------------------------------------

def enrich_chunks_with_visuals(file_path: str, chunks: List[Dict]) -> List[Dict]:
    """
    Extract images + tables from file_path and attach to chunks by page.
    """
    print("\n🖼️  Extracting visuals...")
    images = extract_images(file_path)
    tables = extract_tables(file_path)
    attach_visuals_to_chunks(chunks, images, tables)
    print(f"   Visual enrichment complete.")
    return chunks
