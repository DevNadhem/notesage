# NoteSage

A question-answering assistant for your own notes. Upload PDFs or text files,
ask questions in plain language, and get answers with citations to the source.

## Status
🚧 In development. Sprint 1 (ingestion) is complete: loading and chunking
PDF, text and Markdown files. Next up: Sprint 2 (retrieval).

## Planned features
- Document ingestion (PDF and text)
- Semantic search over your notes
- LLM-generated answers with source citations
- Streamlit web interface

## Supported files
NoteSage currently loads `.pdf`, `.txt` and `.md` files. Each document is
returned as a list of `(page_number, text)` pairs, so later stages can cite
the exact page an answer came from. Plain-text files count as a single page.

## Try the ingestion pipeline
Preview how a document is split into chunks:

```powershell
$env:PYTHONPATH = "src"
python -m notesage.ingest path\to\file.pdf --chunk-size 500 --overlap 50
```

Each chunk keeps its source file, page number and a unique id, which later
stages use to cite where an answer came from.

## Build a search index
Embed your documents and save an index to disk:

```powershell
$env:PYTHONPATH = "src"
python -m notesage.build_index notes.pdf more_notes.md --out data\index
```

The index is stored as `index.faiss` (vectors) plus `chunks.json` (text, source
file and page for each vector). Both live in `data/`, which is git-ignored.
The first run downloads the embedding model (about 90 MB).

## Search your notes
Query a saved index in plain language:

```powershell
$env:PYTHONPATH = "src"
python -m notesage.search data\index "how do plants make food?" -k 3
```

Each result shows its similarity score, source file and page, which is what
the answer step will use for citations.

## Evaluate retrieval
Measure how often the right chunk is found for a set of questions:

```powershell
$env:PYTHONPATH = "src"
python -m notesage.evaluate docs\sample_notes.md --chunk-size 300 --overlap 50
```

Results for different chunk sizes are in `docs/EVALUATION.md`.