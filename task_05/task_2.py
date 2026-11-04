import logging
from pathlib import Path

import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent
MARKDOWN_DIR = ROOT / "data" / "markdown"
MODEL_NAME = "intfloat/multilingual-e5-small"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
TOP_K = 10
logger = logging.getLogger(__name__)


def find_top_similar_chunks(
    model: SentenceTransformer,
    markdown_dir: Path = MARKDOWN_DIR,
    top_k: int = TOP_K,
) -> None:
    r"""Задание 2: выведите top-k самых похожих фрагментов из разных документов.

    1. Загрузите отсортированные Markdown-файлы из markdown_dir.
    2. Разбивайте текст иерархически: сначала по заголовкам уровня ##,
       затем длинные разделы — по абзацам. В RecursiveCharacterTextSplitter
       поставьте разделитель заголовка перед разделителем абзаца.
       Размер — CHUNK_SIZE, перекрытие — CHUNK_OVERLAP.

       Пример параметра separators:

       separators = [
           "\n## ",  # сначала заголовки
           "\n\n",   # затем абзацы
           "\n",
           " ",
           "",
       ]

       Фрагменты короче 128 символов присоедините к соседним.
    3. Посчитайте нормализованные эмбеддинги переданной модели,
       используя префикс passage: и progress bar.
    4. Посчитайте сходство матричным умножением: E @ E.T.
       Оставьте только пары, в которых фрагменты из разных файлов.
    5. Выведите для top-k пар score, имена файлов и тексты фрагментов.

    После запуска оцените насколько по смыслу похожи фрагменты из биографий Толстого А.Н. и Л.Н.
    """
    md_files = sorted(markdown_dir.glob("*.md"))
    if len(md_files) < 2:
        logger.error("Expected at least 2 files in %s", markdown_dir)
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n## ", "\n\n", "\n", " ", ""],
    )

    chunks: list[str] = []
    sources: list[str] = []
    MIN_CHUNK_LEN = 128

    for md_path in md_files:
        text = md_path.read_text(encoding="utf-8")
        file_chunks = splitter.split_text(text)

        merged: list[str] = []
        for chunk in file_chunks:
            if len(chunk) < MIN_CHUNK_LEN and merged:
                merged[-1] = merged[-1] + "\n" + chunk
            else:
                merged.append(chunk)
        if len(merged) > 1 and len(merged[-1]) < MIN_CHUNK_LEN:
            merged[-2] = merged[-2] + "\n" + merged[-1]
            merged.pop()

        chunks.extend(merged)
        sources.extend([md_path.name] * len(merged))

    logger.info("Total chunks: %d (%d files)", len(chunks), len(md_files))

    texts = ["passage: " + c for c in chunks]
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
        convert_to_numpy=True,
    )

    similarities = embeddings @ embeddings.T

    pair_scores: list[tuple[float, int, int]] = []
    n = len(chunks)
    for i in range(n):
        for j in range(i + 1, n):
            if sources[i] != sources[j]:
                pair_scores.append((float(similarities[i, j]), i, j))

    pair_scores.sort(key=lambda x: x[0], reverse=True)

    print(f"\nTop-{top_k} similar chunks from different documents\n")
    for rank, (score, i, j) in enumerate(pair_scores[:top_k], start=1):
        print(f"#{rank}  score={score:.4f} ---")
        print(f"[{sources[i]}] chunk #{i}")
        print(chunks[i][:300].replace("\n", " "))
        print(f"[{sources[j]}] chunk #{j}")
        print(chunks[j][:300].replace("\n", " "))
        print()


def main() -> None:
    """Сравнивает фрагменты Markdown-файлов, подготовленных заданием 1."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    for logger_name in ("transformers", "huggingface_hub", "sentence_transformers", "tokenizers", "httpx"):
        logging.getLogger(logger_name).setLevel(logging.ERROR)
    logger.info("Загрузка модели эмбеддингов: %s", MODEL_NAME)
    model = SentenceTransformer(MODEL_NAME)
    find_top_similar_chunks(model)


if __name__ == "__main__":
    main()
