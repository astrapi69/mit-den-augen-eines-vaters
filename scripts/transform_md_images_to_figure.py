# main.py
import re
import sys
import argparse
from pathlib import Path

def transform_md_images_to_figure(md_text):
    """Wandelt Markdown-Bilder mit optionalen Attributen und Caption-Zeile in <figure> um."""
    img_pattern = r'^!\[(.*?)\]\((.*?)\)(?:\s*\{([^}]*)\})?\s*$'
    lines = md_text.splitlines()
    output_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        img_match = re.match(img_pattern, line)

        if img_match:
            alt = img_match.group(1)
            src = img_match.group(2)
            attrs_str = img_match.group(3)

            # Attribute parsen
            attrs = {}
            if attrs_str:
                for attr in attrs_str.split():
                    if '=' in attr:
                        key, value = attr.split('=', 1)
                        attrs[key] = value

            # Nächste Zeile prüfen: Caption?
            caption = None
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line.startswith('_') and next_line.endswith('_'):
                    caption = next_line[1:-1].strip()
                    if caption.startswith("Figure: "):
                        caption = caption[8:]
                    i += 1  # Caption-Zeile überspringen

            # <img> Tag bauen
            img_attrs = f' src="{src}" alt="{alt}"'
            for key, value in attrs.items():
                img_attrs += f' {key}="{value}"'

            # <figure> Block
            figure = f'''<figure>
  <img{img_attrs} />
'''
            if caption:
                figure += f'''  <figcaption>
    <em>{caption}</em>
  </figcaption>
'''
            figure += '</figure>'

            output_lines.append(figure)
        else:
            output_lines.append(line)

        i += 1

    return '\n'.join(output_lines)


def process_file(input_path: Path, output_path: Path = None):
    """Verarbeitet eine einzelne Datei."""
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    converted = transform_md_images_to_figure(content)

    out_path = output_path or input_path.with_name(input_path.stem + "_converted" + input_path.suffix)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(converted)

    print(f"✅ {input_path} → {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Konvertiert Markdown-Bilder mit Caption in <figure>-Blöcke."
    )
    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="Eine oder mehrere .md-Dateien"
    )
    parser.add_argument(
        "-i", "--inplace",
        action="store_true",
        help="Überschreibt die Originaldateien (Vorsicht!)"
    )

    args = parser.parse_args()

    for file_path in args.files:
        if not file_path.exists():
            print(f"❌ Datei nicht gefunden: {file_path}", file=sys.stderr)
            continue

        if args.inplace:
            process_file(file_path, file_path)
        else:
            process_file(file_path)


if __name__ == "__main__":
    main()