# NoteSage

Ask questions about your own notes and get answers with citations. Upload PDF,
text or Markdown files, and NoteSage retrieves the relevant passages and has a
local language model answer from them, or tells you it couldn't find the answer.

![Answer with a source](docs/screenshots/answer.png)

## Features
- Loads PDF, `.txt` and `.md` files, page by page
- Semantic search with sentence-transformers and a FAISS index
- Answers from a local model through Ollama, so no API key or cloud account
- Cites the file and page behind each answer
- Says "I couldn't find that in your notes" instead of guessing, using a relevance threshold measured from data
- Streamlit web interface and command-line tools

## How it works
1. **Ingest:** files are loaded and split into overlapping chunks that remember their source file and page.
2. **Index:** each chunk is embedded (`all-MiniLM-L6-v2`) and stored in a FAISS inner-product index.
3. **Retrieve:** a question is embedded and the top matching chunks are returned with similarity scores.
4. **Gate:** if the best score is below `MIN_SCORE` (0.25), the model is never called.
5. **Answer:** the remaining chunks go into a prompt that tells the model to use only the notes and cite them; the answer is shown with its sources.

## Setup
Requires Python 3.10+ and [Ollama](https://ollama.com).

```powershell
git clone https://github.com/DevNadhem/notesage.git
cd notesage
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
ollama pull llama3.2
```

The first run downloads the embedding model (about 90 MB).

## Run the web app
```powershell
python -m streamlit run app.py
```
Upload your notes in the sidebar, click **Build index**, and ask questions.

![example notes](docs/screenshots/answer.png)

## Command-line tools
```powershell
$env:PYTHONPATH = "src"
python -m notesage.build_index notes.pdf --out data\index
python -m notesage.search data\index "your question"
python -m notesage.ask data\index "your question"
python -m notesage.evaluate docs\sample_notes.md
python -m notesage.calibrate docs\sample_notes.md --chunk-size 300 --overlap 50
```

## Tests
```powershell
pytest -m "not slow"
```

Upload your notes in the sidebar, click **Build index**, and ask questions.

## Troubleshooting
- **"Ollama is not running"**: start the Ollama app, then reload the page.
- **"Model 'llama3.2' is not installed"**: run `ollama pull llama3.2`.
- **A file was skipped**: the app lists the reason (unsupported type, scanned PDF with no text, unreadable, or too large).
- **"I couldn't find that in your notes"**: the best matching passage scored below the relevance threshold. Try rephrasing, or ask one question at a time.
