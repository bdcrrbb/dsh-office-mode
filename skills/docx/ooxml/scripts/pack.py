# /// script
# requires-python = ">=3.12"
# dependencies = ["defusedxml", "lxml"]
# ///
"""
Tool to pack a directory into a .docx, .pptx, or .xlsx file with XML formatting undone.

Example usage:
    uv run pack.py <input_directory> <office_file> [--force]
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
import defusedxml.minidom
import zipfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Pack a directory into an Office file")
    parser.add_argument("input_directory", help="Unpacked Office document directory")
    parser.add_argument("output_file", help="Output Office file (.docx/.pptx/.xlsx)")
    parser.add_argument("--force", action="store_true", help="Skip validation")
    args = parser.parse_args()

    try:
        success = pack_document(
            args.input_directory, args.output_file, validate=not args.force
        )

        # Show warning if validation was skipped
        if args.force:
            print("Warning: Skipped validation, file may be corrupt", file=sys.stderr)
        # Exit with error if validation failed
        elif not success:
            print("Contents would produce a corrupt file.", file=sys.stderr)
            print("Please validate XML before repacking.", file=sys.stderr)
            print("Use --force to skip validation and pack anyway.", file=sys.stderr)
            sys.exit(1)

    except ValueError as e:
        sys.exit(f"Error: {e}")


def pack_document(input_dir, output_file, validate=False):
    """Pack a directory into an Office file (.docx/.pptx/.xlsx).

    Args:
        input_dir: Path to unpacked Office document directory
        output_file: Path to output Office file
        validate: If True, validates with soffice (default: False)

    Returns:
        bool: True if successful, False if validation failed
    """
    input_dir = Path(input_dir)
    output_file = Path(output_file)

    if not input_dir.is_dir():
        raise ValueError(f"{input_dir} is not a directory")
    if output_file.suffix.lower() not in {".docx", ".pptx", ".xlsx"}:
        raise ValueError(f"{output_file} must be a .docx, .pptx, or .xlsx file")

    # Work in temporary directory to avoid modifying original
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_content_dir = Path(temp_dir) / "content"
        shutil.copytree(input_dir, temp_content_dir)

        # Process XML files to remove pretty-printing whitespace
        for pattern in ["*.xml", "*.rels"]:
            for xml_file in temp_content_dir.rglob(pattern):
                condense_xml(xml_file)

        # Create final Office file as zip archive.
        # OPC/PowerPoint compatibility rules (LibreOffice tolerates violations,
        # PowerPoint does not):
        #   - NO explicit directory entries in the zip
        #   - [Content_Types].xml must exist and be written FIRST
        #   - deterministic entry order after that
        content_types = temp_content_dir / "[Content_Types].xml"
        if not content_types.is_file():
            raise ValueError(
                "[Content_Types].xml not found — cannot build a valid Office file"
            )
        output_file.parent.mkdir(parents=True, exist_ok=True)
        ordered = [content_types]
        ordered += sorted(
            f
            for f in temp_content_dir.rglob("*")
            if f.is_file() and f != content_types
        )
        with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in ordered:
                # files only — never write directory entries
                zf.write(f, f.relative_to(temp_content_dir).as_posix())

        # Structural self-check independent of any validator: catches the
        # classic "opens in LibreOffice, rejected by PowerPoint" breakages.
        check_package_structure(output_file)

        # Validate if requested
        if validate:
            if not validate_document(output_file):
                output_file.unlink()  # Delete the corrupt file
                return False

    return True


def check_package_structure(doc_path):
    """Assert OPC zip-structure rules PowerPoint enforces but LibreOffice ignores."""
    with zipfile.ZipFile(doc_path) as zf:
        names = zf.namelist()
        if any(name.endswith("/") for name in names):
            raise ValueError(
                "zip contains explicit directory entries — PowerPoint rejects "
                "these. Repack with pack.py, never with `zip -r`."
            )
        if not names or names[0] != "[Content_Types].xml":
            raise ValueError("[Content_Types].xml must be the first zip entry")


def validate_document(doc_path):
    """Validate document strictly, then with soffice.

    soffice (LibreOffice) is LENIENT: it happily opens files PowerPoint
    rejects (bad content types, broken rels, extra dir entries). So the
    strict check runs FIRST via the format library (python-pptx /
    python-docx / openpyxl), which parses the OPC package — content
    types, rels, part graph — much the way PowerPoint's own reader does.
    """
    if not strict_library_check(doc_path):
        return False
    return soffice_check(doc_path)


def strict_library_check(doc_path):
    """Open the package with the format's strict reference library."""
    suffix = doc_path.suffix.lower()
    try:
        if suffix == ".pptx":
            from pptx import Presentation

            prs = Presentation(str(doc_path))
            _ = len(prs.slides._sldIdLst)  # force full part graph walk
        elif suffix == ".docx":
            import docx

            d = docx.Document(str(doc_path))
            _ = len(d.paragraphs)
        elif suffix == ".xlsx":
            import openpyxl

            wb = openpyxl.load_workbook(str(doc_path), read_only=True)
            _ = wb.sheetnames
        else:
            print(f"Warning: no strict checker for {suffix}", file=sys.stderr)
        print("Strict package check passed", file=sys.stderr)
        return True
    except ImportError:
        # library missing: warn loudly, rely on soffice below
        print(
            f"Warning: strict {'python-pptx' if suffix=='.pptx' else 'python-docx' if suffix=='.docx' else 'openpyxl'}"
            " not installed — falling back to lenient soffice check only",
            file=sys.stderr,
        )
        return True
    except Exception as e:
        print(f"Validation error (strict package check): {e}", file=sys.stderr)
        return False


def soffice_check(doc_path):
    # Determine the correct filter based on file extension
    match doc_path.suffix.lower():
        case ".docx":
            filter_name = "html:HTML"
        case ".pptx":
            filter_name = "html:impress_html_Export"
        case ".xlsx":
            filter_name = "html:HTML (StarCalc)"

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            result = subprocess.run(
                [
                    "soffice",
                    "--headless",
                    "--convert-to",
                    filter_name,
                    "--outdir",
                    temp_dir,
                    str(doc_path),
                ],
                capture_output=True,
                timeout=30,
                text=True,
            )
            if not (Path(temp_dir) / f"{doc_path.stem}.html").exists():
                error_msg = result.stderr.strip() or "Document validation failed"
                print(f"Validation error: {error_msg}", file=sys.stderr)
                return False
            return True
        except FileNotFoundError:
            print("Warning: soffice not found. Skipping validation.", file=sys.stderr)
            return True
        except subprocess.TimeoutExpired:
            print("Validation error: Timeout during conversion", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Validation error: {e}", file=sys.stderr)
            return False


def condense_xml(xml_file):
    """Strip unnecessary whitespace and remove comments."""
    with open(xml_file, "r", encoding="utf-8") as f:
        dom = defusedxml.minidom.parse(f)

    # Process each element to remove whitespace and comments
    for element in dom.getElementsByTagName("*"):
        # Skip w:t elements and their processing
        if element.tagName.endswith(":t"):
            continue

        # Remove whitespace-only text nodes and comment nodes
        for child in list(element.childNodes):
            if (
                child.nodeType == child.TEXT_NODE
                and child.nodeValue
                and child.nodeValue.strip() == ""
            ) or child.nodeType == child.COMMENT_NODE:
                element.removeChild(child)

    # Write back the condensed XML
    with open(xml_file, "wb") as f:
        f.write(dom.toxml(encoding="UTF-8"))


if __name__ == "__main__":
    main()
