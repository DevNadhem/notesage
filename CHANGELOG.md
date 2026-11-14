# Changelog

## [Unreleased] - Sprint 2: Retrieval
### Added
- `Embedder` class wrapping sentence-transformers (`all-MiniLM-L6-v2`) with lazy loading and normalized output
## Build a search index
Embed your documents and save an index to disk:

```powershell
$env:PYTHONPATH = "src"
python -m notesage.build_index notes.pdf more_notes.md --out data\index
```

The index is stored as `index.faiss` (vectors) plus `chunks.json` (text, source
file and page for each vector). Both live in `data/`, which is git-ignored.
The first run downloads the embedding model (about 90 MB).

## [0.1.0] - Sprint 1: Ingestion
### Added
- PDF loader with page-by-page text extraction (`load_pdf`)
- Plain-text and Markdown loader (`load_text`)
- `load_document` dispatcher that returns `(page_number, text)` pairs
- Overlapping chunker (`chunk_text`) and `Chunk` dataclass with source and page metadata
- `python -m notesage.ingest` CLI to preview chunks
- Unit tests for loaders and chunker (22 tests)
- pytest configuration

### Notes
- Sprints are compressed to fit a Monday deadline (see `docs/ROADMAP.md`).

