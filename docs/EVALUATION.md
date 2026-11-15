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

## Not-found threshold
Measured with `python -m notesage.calibrate docs\sample_notes.md --chunk-size 300 --overlap 50`
on 14 answerable and 10 unanswerable questions.

- Lowest top score among answerable questions: 0.34
- Highest top score among unanswerable questions: 0.22
- Chosen `MIN_SCORE`: 0.25

Reason: the ranges do not overlap, so any value between 0.22 and 0.34 separates
them on this data. 0.25 blocks every unanswerable question while leaving a
margin below the weakest answerable one, because wrongly refusing a valid
question is worse than sending an extra off-topic question to the model.
The closest case was "How many moons does Mars have?" (0.22), which is near the
astronomy notes. Results come from a small notes file and may shift with other
documents.