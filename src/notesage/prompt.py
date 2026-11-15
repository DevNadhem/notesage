DEFAULT_MAX_CONTEXT_CHARS = 3000
NOT_FOUND_MESSAGE = "I couldn't find that in your notes."


def format_chunk(number, result):
    """Format one search result as a numbered, citable block."""
    chunk = result.chunk
    return f"[{number}] ({chunk.source}, page {chunk.page})\n{chunk.text}"


def build_context(results, max_chars=DEFAULT_MAX_CONTEXT_CHARS):
    """Join numbered chunks, stopping before the character budget is exceeded.

    Results are expected best-first, so the least relevant ones are dropped.
    If even the first block is too long, it is cut to fit.
    """
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")

    blocks = []
    used = 0
    for number, result in enumerate(results, start=1):
        block = format_chunk(number, result)
        separator = 2 if blocks else 0  # the blank line between blocks
        if used + separator + len(block) > max_chars:
            if not blocks:
                blocks.append(block[:max_chars])
            break
        blocks.append(block)
        used += separator + len(block)
    return "\n\n".join(blocks)

PROMPT_TEMPLATE = """You answer questions using only the notes provided below.

Rules:
- Use only the information in the notes. Do not use outside knowledge.
- Cite the notes you used by number, like [1] or [2].
- If the notes do not contain the answer, reply exactly: {not_found}

Notes:
{context}

Question: {question}

Answer:"""


def build_prompt(question, results, max_context_chars=DEFAULT_MAX_CONTEXT_CHARS):
    """Build the full prompt for the LLM from a question and search results."""
    question = question.strip()
    if not question:
        raise ValueError("question must not be empty")
    if not results:
        raise ValueError("no search results to build a prompt from")

    return PROMPT_TEMPLATE.format(
        not_found=NOT_FOUND_MESSAGE,
        context=build_context(results, max_context_chars),
        question=question,
    )