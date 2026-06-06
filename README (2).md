# Self-Contradiction Detector
### Protofine.ai — AI/ML Engineering Internship Task
**Author:** Jeevan

> **Zero dependencies. No API key. Runs offline. Pure Python 3.10+.**

---

## What I Built

A Python tool that takes any AI-generated text and detects **self-contradictions** — places where the same answer makes two claims that logically cannot both be true.

The detector uses a **5-layer rule-based engine** written entirely in the Python standard library. No LLM call, no internet, no API key. It returns structured JSON with a flag, severity score, confidence level, the two conflicting sentences, and every rule that fired.

A web demo (HTML/JS) ships alongside the Python code — same engine, ported to JavaScript, running entirely in the browser.

---

## Project Structure

```
contradiction-detector/
├── detector.py           # Core rule engine — 5 detection layers
├── main.py               # CLI: --check / --test / --guide
├── requirements.txt      # Empty — zero dependencies
├── Dockerfile
└── tests/
    ├── test_cases.py     # 6 hand-crafted test cases
    ├── run_tests.py      # Test runner + precision/recall/F1
    └── test_results.json # Output from last run
```

---

## Setup & Run

**No install needed beyond Python 3.10+**

```bash
# Check a piece of text
python main.py --check "Redis never writes to disk. Redis uses AOF logs to write to disk."

# Run the full test suite
python main.py --test

# Show the prompt guide
python main.py --guide
```

**With Docker:**
```bash
docker build -t contradiction-detector .
docker run contradiction-detector python main.py --test
```

---

## Sample Output

```json
{
  "flag": true,
  "score": 75,
  "confidence": "high",
  "checks": [
    {"rule": "antonym_pair", "detail": "\"stateless\" (sentence 1) directly opposes \"memory of\" (sentence 3)."},
    {"rule": "absolute_negation_flip", "detail": "Sentence 1 uses absolute \"no\" but sentence 3 contradicts it on shared subject \"memory\"."}
  ],
  "quote_a": "Transformer models are inherently stateless — each forward pass processes the input independently with no memory of previous inputs.",
  "quote_b": "The attention mechanism allows transformers to maintain and update a running state across tokens in a sequence, effectively giving the model memory of earlier tokens.",
  "reason": "Strong contradiction found (score 75/100). 2 rule(s) fired. Two or more claims are logically mutually exclusive."
}
```

---

## The 5-Layer Rule Engine

| Layer | Name | Score | What it catches |
|-------|------|-------|-----------------|
| 1 | Antonym-pair scanner | +40 | 40+ known opposite pairs: `stateless/stateful`, `never writes/writes to disk`, `safe indefinitely/should not`, etc. |
| 2 | Absolute-negation flip | +35 | "never/always/completely X" in one sentence contradicted by another on the same subject |
| 3 | Quantity contradiction | +30 | "zero/none" vs a non-zero claim; "all/every" vs "sometimes/in some cases" |
| 4 | Scope violation | +25 | Universal claim ("in all cases") followed by a scoped exception ("under certain conditions") |
| 5 | Shared-subject negation | +20 | Two sentences sharing key nouns — one asserts, one denies |

**Confidence tiers:** score ≥60 → high · 35–59 → medium · <35 → low

---

## Test Results (actual run output)

```
══════════════════════════════════════════════════════════════
   CONTRADICTION DETECTOR — TEST SUITE  (no API required)
══════════════════════════════════════════════════════════════

▸ Case 1: Clear technical contradiction        easy    ✅ PASS  score=35  medium
▸ Case 2: Python GIL explanation (clean)       easy    ✅ PASS  score=0   clean
▸ Case 3: Transformer statefulness (tricky)    hard    ✅ PASS  score=75  high
▸ Case 4: Ibuprofen safety                     medium  ✅ PASS  score=40  medium
▸ Case 5: ML data scaling (nuance trap)        medium  ✅ PASS  score=0   clean
▸ Case 6: Privacy policy                       medium  ✅ PASS  score=70  high

   RESULTS : 6/6 passed  |  0 failed
   TP=4  FP=0  FN=0  TN=2
   Precision : 1.00   Recall : 1.00   F1 : 1.00
══════════════════════════════════════════════════════════════
```

**Case 3 is the key "tricky" case.** The transformer text confidently asserts "inherently stateless" and "no memory of previous inputs", then describes attention giving "memory of earlier tokens". Both halves sound expert-level — neither hedges. This is the confident-wrong pattern the task targets.

**Case 5 is the false-positive trap.** ML data scaling with "generally more data helps... but diminishing returns" correctly scores 0. The engine does not flag nuance.

---

## Why Self-Contradiction?

I chose self-contradiction over fabricated statistics or fake citations for two reasons:

**1. It requires reasoning, not retrieval.** A fabricated stat can sometimes be Googled. A contradiction detector must understand what claims *mean*, map their logical relationships, and determine mutual exclusivity. That's closer to real metacognition.

**2. It's invisible to sequential readers.** An AI answer can contradict itself across two paragraphs while sounding perfectly authoritative throughout. Readers process sentences sequentially and miss cross-paragraph conflicts entirely.

---

## Key Design Decisions

**1. Rule-based over LLM-based.** A rule engine is deterministic — the same input always produces the same output. An LLM detector would vary between runs (temperature > 0) and require an API key, adding friction and cost. For a reliability tool, determinism matters more than language understanding breadth.

**2. Scoring over binary flag.** A single true/false verdict loses information. The 0–100 score lets downstream systems treat high-confidence flags as automatic rejections and route low-confidence ones to human review.

**3. Verbatim quote extraction.** The output returns the actual contradicting sentences, not a paraphrase. Reviewers can jump straight to the conflict without re-reading the full text.

**4. Explicit false-positive guards.** The antonym pairs are specific (e.g. `"safe for long-term"` not just `"safe"`) to avoid flagging legitimate qualifications. The nuance trap in Case 5 confirms this works.

**5. Prompt guide built in.** Running `python main.py --guide` teaches users what a contradiction actually is, how to write text for best results, and what this tool does not catch. Teaching correct usage is part of building a trustworthy system.

---

## Where the AI Gave Wrong Output — And How I Fixed It

During early prototyping with an LLM-based approach, the model flagged nuanced text like *"Machine learning generally improves with more data, but there are diminishing returns"* as a contradiction between "improves with data" and "diminishing returns."

This is wrong — both claims are simultaneously true and standard ML knowledge.

**Fix:** I replaced the LLM backend entirely with a deterministic rule engine, and made the antonym pairs deliberately specific. Instead of matching the broad word `"safe"`, the engine matches `"safe for long-term"` — which only fires when a categorical safety claim is present, not any mention of safety. Case 5 (the nuance trap) now correctly scores 0 every time.

---

## Reliability Note — How to Measure This Detector

### The Core Problem

Running it on 6 hand-crafted cases tells us it works on those 6 cases. It tells us almost nothing about performance on the real distribution of AI answers.

### What We'd Need

A benchmark dataset of 200–500 AI-generated answers with ground-truth contradiction labels, across:
- Domains: technical, medical, legal, policy, general
- Difficulty: obvious, subtle, tricky (confident-sounding)
- Clean examples: nuance traps, legitimate hedges, temporal changes

Each labeled by multiple human annotators with inter-annotator agreement (Cohen's κ). Disagreements reveal the hard edge of what "contradiction" means.

### Metrics That Matter

| Metric | Why it matters here |
|--------|---------------------|
| **Precision** | Low precision = users stop trusting the tool after too many false alarms |
| **Recall** | Low recall = dangerous — missed contradictions in medical/legal contexts cause real harm |
| **F1** | Overall balance |
| **False Positive Rate** | Critical for trust in a safety tool |

For a trust/safety tool, **recall > precision** — missing a real contradiction is worse than an extra false alarm.

### False-Positive Risk Areas

1. **Qualified statements** — "X is generally true... but not always." Both halves are simultaneously true. Mitigated by requiring specific antonym phrases, not broad word matches.
2. **Temporal statements** — "In 2020, policy was X. Today it's Y." Not a contradiction; reflects change over time. The engine may flag without temporal context.
3. **Domain-specific idioms** — Some technical fields have terminology that looks contradictory out of context. A domain-aware version would filter these.
4. **Figurative language** — "Both a blessing and a curse." Not a logical contradiction. The current engine handles this by requiring keyword-level specificity.

### Current Limitations

- 6 test cases is a proof of concept, not a reliability measurement
- The antonym pair list covers common cases but is not exhaustive
- Performance on domains outside the current pair list (e.g. legal, financial) is untested

### Next Steps to Improve

1. Build a 200-case benchmark with human labels
2. Add domain-specific antonym pair modules (medical, legal, finance)
3. Add a second-pass check: for any firing pair, verify shared subject before flagging
4. Consider ensemble: two independent rule passes, only flag if both agree

---

## License

MIT
