# Witness-preserving decomposition for developer documentation

A research prototype and frozen evidence set for exact, source-relative documentation claims. A claim that a release, interpreter tag, and platform tag occur on **one artifact** is stronger than three independently successful pair checks.

This repository implements shared-row witness binding and controlled factual rendering. Its mathematical basis is established relational provenance and lossless/lossy projection semantics. It does not claim a new database theorem, first discovery of relational hallucination, or production deployment.

## Executed evidence

- Frozen PyPI metadata: 30 preselected packages, 28 usable CPython-tag relations, 12,243 distinct tuples.
- 152 absent triples with all three pairs present, across 14 packages.
- 121 matched pairs (242 claims), constructed from real publication records; an enriched stress set, not natural error prevalence.
- Independent SQL labels and 1,452 binding checks across six decompositions; all passed.
- Exhaustive uncertainty labels: 256 binary ternary relations, 166 view classes, 1,328 query/class checks; all passed.
- 10 functional/adversarial unit tests; all passed.
- Actual local inference: 120 Qwen3 restricted-label calls; 36 Qwen2.5-Coder restricted-label calls; 84 Qwen2.5-Coder free-generation calls; 28 natural-planner calls. All raw prompts and responses are retained.

The planner control returns field/value pairs instead of the requested field-name schema (0/28 strict compliance). A separately reported post-hoc normalization recovers all 28 as whole-row lookups, with 28 correct controlled sentences. This is **not evidence that natural planners commonly choose harmful decomposition**. The local-model results are small diagnostics and do not establish superiority over other factuality systems.

## Reproduce exact checks

Python 3.10+; no GPU or model download needed:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s src -p 'test_*.py'
python src/check_views.py
python src/exhaustive.py
python src/analyze.py
python src/analyze_controls.py
python src/cli.py --task-id aiohttp-0-no
```

The CLI emits a typed decision, frozen-snapshot identifier, witness if supported, and a controlled sentence. It never asserts runtime installability.

## Reproduce inference

On Apple silicon, install `requirements-inference.txt`. Download pinned MLX conversions into separate local directories:

| Model | Hugging Face revision |
|---|---|
| `mlx-community/Qwen3-4B-Instruct-2507-4bit` | `50d427756c6b1b2fe0c0a10f67fbda1fc8e82c1b` |
| `mlx-community/Qwen2.5-Coder-7B-Instruct-4bit` | `019cc73c45c770444708a6dd8690c66243cc5c80` |

Run each separately; do not overwrite the released trace files:

```sh
python src/run_views.py --model /path/to/qwen3 --output /tmp/qwen3-reproduction.jsonl --limit 40
python src/run_views.py --model /path/to/qwen25 --output /tmp/qwen25-reproduction.jsonl --limit 12
python src/run_reasoned.py --model /path/to/qwen25
python src/run_workflow.py --model /path/to/qwen25 --limit-packages 14
```

The last two commands resume released completed traces without new calls. Move their JSONL outputs aside in your own reproduction checkout before regenerating. Greedy inference and exact prompts are recorded, but bitwise model reproducibility across runtime and hardware versions is not guaranteed. The original run used MLX 0.32.3 and mlx-lm 0.32.0 on a 24-GiB Apple-silicon Mac.

## Data and source boundaries

`data/relations.json` retains the filtered tuples and original wheel filenames. `data/sources.json` records URLs, selected versions, and original metadata hashes. `data/tasks.jsonl` includes contexts, matched-pair identities, full-source labels, and evidence-relative uncertainty labels. The raw PyPI project descriptions and model weights are excluded.

`fetch_snapshot.py` collects a **new** live snapshot. `build_corpus.py` builds relations and cases from that download. Live releases change; these operations do not reproduce the old corpus. Exact verification uses the frozen derived data already in the repository.

A positive claim concerns literal published wheel tags, existentially projecting away ABI. A negative claim concerns absence in the stated source. Neither is a claim about installability, source builds, transitive dependency resolution, or package support policy. A snapshot hash is not source authentication. The reference binder recomputes witnesses from the full source; direct SQL is an equally correct and simpler alternative for a standalone structured lookup.

## Related work

The contribution must be read alongside Green et al., *Provenance Semirings* (PODS 2007); Fatahi Bayat et al., *FLEEK* (EMNLP 2023); Liu et al., *BeyondAtoms/CARVE* (2026 author-released manuscript); Alvarez et al., *ProvenanceGuard* (arXiv:2606.18037); Buchmann and Gurevych, *Citation Failure* (TACL 2026); and Feng et al., *Hyper-RAG* (Nature Communications 2026). These establish that provenance, relational factuality, and higher-order evidence are prior art.

This artifact accompanies NAACL 2027 Industry Track submission #22, submitted October 12, 2026. It has not been accepted or peer reviewed. Submission record: https://openreview.net/forum?id=8xuQ6eMaGE.
