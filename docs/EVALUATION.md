# Retrieval evaluation

Measured with `python -m notesage.evaluate docs\sample_notes.md` on the 14
questions in `docs/eval_questions.json`. A hit means one of the top-k chunks
comes from the right file and contains the answer phrase.

| chunk_size | overlap | chunks | hit@1 | hit@3 |
|---|---|---|---|---|
| 500 | 50 | 5 | 100 | 100 |
| 300 | 50 | 8 | 93 | 100 |
| 200 | 40 | 12 | 86 | 100 |

## Decision
Write one or two sentences: which setting did best and whether you are keeping
the defaults (500/50) or recommending a different value. If the results are
close, say so and keep the defaults.

## Limitations
- 14 questions on one small file is a sanity check, not a benchmark.
- A hit checks for a phrase in the chunk, so it can't tell whether the chunk
  fully answers the question.