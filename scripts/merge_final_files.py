import os
from pathlib import Path

# Change working directory to project root (parent directory of scripts/)
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir("..")

BOOK_DIR = Path("./manuscript")
SECTIONS = ["front-matter", "chapters", "back-matter"]
SUFFIX = "-final.md"


def merge_final_versions():
    for section in SECTIONS:
        section_path = BOOK_DIR / section
        if not section_path.exists():
            continue

        for original_file in section_path.glob("*.md"):
            # Skip files that are already final or backups
            if original_file.name.endswith(SUFFIX) or original_file.name.endswith(".md.bak"):
                continue

            final_file = section_path / (original_file.stem + SUFFIX)

            if not final_file.exists():
                print(f"⏭️ Skipped: {original_file.name} (no {final_file.name} found)")
                continue

            # Backup and overwrite
            backup_file = original_file.with_suffix(".md.bak")
            original_file.rename(backup_file)
            final_file.rename(original_file)

            print(f"📝 Merged: {final_file.name} → {original_file.name} (backup saved as {backup_file.name})")


if __name__ == "__main__":
    merge_final_versions()
