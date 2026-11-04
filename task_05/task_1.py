import logging
import re
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
MARKDOWN_DIR = DATA_DIR / "markdown"
PDF_PATHS = (DATA_DIR / "Толстой_ЛН.pdf", DATA_DIR / "Толстой_АН.pdf")


def clean_text(text: str) -> str:
    """Задание 1: объедините соседние заголовки ## и удалите URL, сохранив подписи ссылок."""
    lines = text.splitlines()
    merged_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("## "):
            header_parts = [line[3:].strip()]
            j = i + 1
            while j < len(lines) and lines[j].startswith("## "):
                header_parts.append(lines[j][3:].strip())
                j += 1
            combined = "## " + " ".join(header_parts)
            merged_lines.append(combined)
            i = j
        else:
            merged_lines.append(line)
            i += 1

    text = "\n".join(merged_lines)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    return text


def convert_pdf_to_markdown(pdf_path: Path, output_path: Path) -> None:
    """Задание 1: распознайте PDF через Docling и сохраните очищенный Markdown."""
    # Подсказка: отключите OCR и распознавание таблиц в PdfPipelineOptions.
    # Преобразуйте результат через document.export_to_markdown(), затем очистите его.
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = False

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    result = converter.convert(pdf_path)
    markdown = result.document.export_to_markdown()
    cleaned = clean_text(markdown)
    output_path.write_text(cleaned, encoding="utf-8")


def main() -> None:
    """Распознаёт оба PDF и записывает Markdown в data/markdown/."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)
    for pdf_path in PDF_PATHS:
        output_path = MARKDOWN_DIR / f"{pdf_path.stem}.md"
        logging.info("Обработка %s → %s", pdf_path.name, output_path.relative_to(ROOT))
        convert_pdf_to_markdown(pdf_path, output_path)


if __name__ == "__main__":
    main()
