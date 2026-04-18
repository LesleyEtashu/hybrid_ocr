import re
import json
from pathlib import Path
from datetime import datetime, timezone


def process_single_file(input_file: Path, document_name: str):

    # Extract model name from filename
    model_name = input_file.stem.replace("_output", "")

    output_folder = Path("datasets") / model_name
    output_folder.mkdir(parents=True, exist_ok=True)

    try:
        content = input_file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = input_file.read_text(encoding="latin-1")

    page_pattern = r'(?:---\s*\n)?#{0,6}\s*[Pp]age[_ ](\d+)\s*\n(?:---\s*\n)?'
    parts = re.split(page_pattern, content)

    if len(parts) < 3:
        print(f"Skipping {input_file.name} (no page markers found)")
        return

    total_pages = (len(parts) - 1) // 2

    document_result = {
        "model_name": model_name,
        "document_name": document_name,
        "total_pages": total_pages,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pages": []
    }

    for i in range(1, len(parts), 2):
        page_number = int(parts[i])
        page_content = parts[i + 1].strip()

        document_result["pages"].append({
            "page_number": page_number,
            "content": page_content,
            "metadata": {
                "confidence": None
            }
        })

    output_file = output_folder / f"{input_file.stem}_document.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(document_result, f, ensure_ascii=False, indent=2)

    print(f"Processed {input_file.name} → datasets/{model_name}/")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage:")
        print("python json-script.py <output_folder> <document_name>")
        exit(1)

    root_folder = Path(sys.argv[1])
    document_name = sys.argv[2]

    for input_file in root_folder.glob("*.md"):
        process_single_file(input_file, document_name)