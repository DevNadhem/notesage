# Changelog

## [Unreleased] - Sprint 3: Generation
### Added
- Prompt template that numbers retrieved chunks, restricts the model to the notes, asks for citations and defines a fixed "not found" reply
- Context truncation to a configurable character limit
- `OllamaClient` for local models via Ollama (standard library only) with clear errors when the server is unreachable
- `answer_question` pipeline that retrieves chunks, builds the prompt, calls the model and returns the answer with its sources
- `python -m notesage.ask` CLI

## [0.2.0] - Sprint 2: Retrieval
### Added
- `Embedder` class wrapping sentence-transformers (`all-MiniLM-L6-v2`) with lazy loading and normalized output
- `VectorIndex` (FAISS inner-product index) with chunk metadata, plus `save`/`load` persistence
- `python -m notesage.build_index` CLI to build and save an index from documents
- `VectorIndex.search` returns the top-k chunks with cosine similarity scores, capped at the index size
- `python -m notesage.search` CLI to query a saved index
- `python -m notesage.evaluate` reports hit@1 and hit@3 on a question set, with sample notes and questions in `docs/`
- Retrieval evaluation results in `docs/EVALUATION.md`

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

