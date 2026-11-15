import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from notesage.answer import answer_question  # noqa: E402
from notesage.embeddings import Embedder  # noqa: E402
from notesage.llm import LLMError, OllamaClient  # noqa: E402
from notesage.service import NoteSageError, build_index_from_uploads  # noqa: E402

st.set_page_config(page_title="NoteSage", page_icon="📝")
st.title("📝 NoteSage")
st.caption("Ask questions about your own notes and get answers with sources.")


@st.cache_resource
def get_embedder():
    return Embedder()


with st.sidebar:
    st.header("Your notes")
    uploads = st.file_uploader(
        "Upload PDF, text or Markdown files",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
    )
    if st.button("Build index", disabled=not uploads):
        with st.spinner("Reading and indexing your notes..."):
            try:
                files = [(f.name, f.getvalue()) for f in uploads]
                index, skipped = build_index_from_uploads(files, get_embedder())
            except NoteSageError as exc:
                st.error(str(exc))
            else:
                st.session_state["index"] = index
                st.session_state["messages"] = []
                st.success(f"Indexed {len(index)} chunks from {len(uploads)} file(s).")
                for note in skipped:
                    st.warning(note)

if "index" not in st.session_state:
    st.info("Upload your notes in the sidebar and click **Build index** to start.")
    st.stop()

for message in st.session_state.get("messages", []):
    with st.chat_message(message["role"]):
        st.write(message["text"])
        for source in message.get("sources", []):
            st.caption(f"Source: {source}")

question = st.chat_input("Ask a question about your notes")
if question:
    st.session_state["messages"].append({"role": "user", "text": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = answer_question(
                    question, st.session_state["index"], get_embedder(), OllamaClient()
                )
                text = result.text
                sources = [
                    f"{s.chunk.source}, page {s.chunk.page}" for s in result.sources
                ]
            except LLMError as exc:
                text, sources = f"Sorry, the language model failed: {exc}", []
        st.write(text)
        for source in sources:
            st.caption(f"Source: {source}")
    st.session_state["messages"].append(
        {"role": "assistant", "text": text, "sources": sources}
    )