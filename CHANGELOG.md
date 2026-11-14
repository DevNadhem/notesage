# Changelog

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