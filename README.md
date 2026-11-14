# NoteSage

A question-answering assistant for your own notes. Upload PDFs or text files,
ask questions in plain language, and get answers with citations to the source.

## Status
🚧 In development. Currently in Sprint 0 (setup).

## Planned features
- Document ingestion (PDF and text)
- Semantic search over your notes
- LLM-generated answers with source citations
- Streamlit web interface

## Supported files
NoteSage currently loads `.pdf`, `.txt` and `.md` files. Each document is
returned as a list of `(page_number, text)` pairs, so later stages can cite
the exact page an answer came from. Plain-text files count as a single page.
