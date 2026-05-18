"""Convert a .docx to .pdf via LibreOffice headless, with Word AppleScript fallback."""

import shutil
import subprocess
from pathlib import Path


def export_pdf(docx_path, out_dir=None):
    """Render docx_path to PDF. Returns path to the produced PDF.

    Tries soffice (LibreOffice) first; falls back to Microsoft Word via
    AppleScript on macOS if soffice is unavailable or fails.
    """
    docx_path = Path(docx_path).resolve()
    out_dir = Path(out_dir).resolve() if out_dir else docx_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / (docx_path.stem + ".pdf")

    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice:
        try:
            subprocess.run(
                [soffice, "--headless", "--convert-to", "pdf",
                 "--outdir", str(out_dir), str(docx_path)],
                check=True, capture_output=True, timeout=180,
            )
            if pdf_path.exists():
                return pdf_path
        except subprocess.CalledProcessError as e:
            print(f"soffice failed: {e.stderr.decode()[:200]}")

    # Word fallback (macOS)
    try:
        ascript = f'''
        tell application "Microsoft Word"
            set theDoc to open file (POSIX file "{docx_path}" as alias)
            save as theDoc file name "{pdf_path}" file format format PDF
            close theDoc saving no
        end tell
        '''
        subprocess.run(["osascript", "-e", ascript], check=True, capture_output=True, timeout=180)
        if pdf_path.exists():
            return pdf_path
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    raise RuntimeError(f"Could not convert {docx_path} to PDF; install LibreOffice or Word.")


if __name__ == "__main__":
    import sys
    out = export_pdf(sys.argv[1])
    print(f"Wrote {out}")
