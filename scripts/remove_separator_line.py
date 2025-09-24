#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
from pathlib import Path

def find_and_remove_separators(lines):
    """Remove '---' lines ONLY when:
    - Previous line is empty or whitespace-only
    - Current line is exactly '---'
    - Next line starts with '#' (header)
    Returns new lines and list of removed line numbers (1-indexed).
    """
    new_lines = []
    i = 0
    removed_lines = []

    while i < len(lines):
        # Need context: at least one line before and after
        if i > 0 and i + 1 < len(lines):
            # Normalize all three lines
            prev_line = lines[i-1].rstrip('\r\n')
            current_line = lines[i].rstrip('\r\n')
            next_line = lines[i+1].rstrip('\r\n').lstrip()  # lstrip to ignore indentation

            # Check strict pattern
            if (current_line == '---' and
                    prev_line.strip() == '' and    # prev line is blank (allow spaces)
                    next_line.startswith('#')):    # next line starts with #

                removed_lines.append(i + 1)    # record 1-indexed line number
                i += 1                         # skip current line → remove it
                continue

        # Keep current line
        new_lines.append(lines[i])
        i += 1

    return new_lines, removed_lines

def process_md_file(filepath, dry_run=False, verbose=False, in_place=False):
    """Process file to remove separator lines matching the strict pattern."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return False

    new_lines, removed_lines = find_and_remove_separators(lines)

    if len(removed_lines) == 0:
        if verbose:
            print(f"ℹ️  No separator lines found in {filepath}")
        return True

    # Create backup ONLY if not in-place and not dry-run
    if not in_place and not dry_run:
        backup_path = str(filepath) + '.bak'
        if not os.path.exists(backup_path):
            try:
                with open(filepath, 'r', encoding='utf-8') as src, \
                        open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.writelines(lines)
                if verbose:
                    print(f"💾 Backup saved: {backup_path}")
            except Exception as e:
                print(f"⚠️  Could not create backup for {filepath}: {e}")

    if dry_run:
        print(f"📄 DRY RUN — {filepath} would remove {len(removed_lines)} line(s):")
        for line_num in removed_lines:
            print(f"   Line {line_num}: '---'")
    else:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"✅ Removed {len(removed_lines)} separator line(s) from: {filepath}")
        except Exception as e:
            print(f"❌ Error writing to {filepath}: {e}")
            return False

    return True

def collect_files(paths, recursive=True):
    """Collect all .md files from given paths (files or folders)."""
    md_files = []
    for path in paths:
        p = Path(path)
        if p.is_file() and p.suffix.lower() == '.md':
            md_files.append(p)
        elif p.is_dir():
            pattern = '**/*.md' if recursive else '*.md'
            md_files.extend(p.glob(pattern))
        else:
            print(f"⚠️  Warning: {path} is not a valid file or directory.")
    return md_files

def main():
    parser = argparse.ArgumentParser(
        description="Strictly remove '---' lines ONLY when: blank line above, and header (#) below."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Paths to .md files or folders to process. Default: current directory."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files."
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Do not search subdirectories recursively."
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed messages (e.g., files with no matches)."
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Edit files in-place without creating .bak backup files."
    )

    args = parser.parse_args()

    md_files = collect_files(args.paths, recursive=not args.no_recursive)

    if not md_files:
        print("❌ No .md files found!")
        return

    print(f"🔍 Found {len(md_files)} .md file(s) to process")
    print("✂️  Removing '---' ONLY when:\n     • Line above is blank\n     • Line below starts with '#'\n     • Line is exactly '---'")
    if args.dry_run:
        print("🧪 DRY RUN — No files will be modified.")
    if args.in_place:
        print("⚡ IN-PLACE MODE — No backup (.bak) files will be created.")
    print("-" * 75)

    success_count = 0
    for md_file in md_files:
        if process_md_file(
                md_file,
                dry_run=args.dry_run,
                verbose=args.verbose,
                in_place=args.in_place
        ):
            success_count += 1

    print("-" * 75)
    print(f"🎉 Done! {success_count}/{len(md_files)} file(s) processed successfully.")

if __name__ == "__main__":
    main()