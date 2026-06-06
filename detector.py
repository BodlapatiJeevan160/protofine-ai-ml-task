"""
Self-Contradiction Detector — Rule-Based Engine
Protofine.ai · AI/ML Engineering Internship Task
Author: Jeevan

No API key required. Runs entirely on pure Python with zero dependencies.
Five detection layers: antonym pairs, absolute-negation flip, quantity
contradiction, scope violation, shared-subject negation.
"""

import re
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# KNOWLEDGE BASE — 5 layers of contradiction rules
# ─────────────────────────────────────────────────────────────────────────────

# Layer 1: Known antonym pairs — (phrase_a, phrase_b)
# If sentence i contains phrase_a AND sentence j contains phrase_b → flag
ANTONYM_PAIRS = [
    # Memory / state
    ("stateless", "stateful"),
    ("stateless", "stores state"),
    ("stateless", "maintains state"),
    ("stateless", "memory of"),
    ("no memory", "has memory"),
    ("no memory", "memory of"),
    ("no state", "keeps state"),
    ("no state", "maintains state"),
    ("independent", "dependent on previous"),
    # Disk / persistence
    ("never writes", "writes"),
    ("never write", "write to disk"),
    ("never stored", "stored on"),
    ("not persisted", "persisted"),
    ("ephemeral", "persistent"),
    ("lost on restart", "survives restart"),
    ("lost when", "durable"),
    # Safety / risk
    ("always safe", "unsafe"),
    ("always safe", "dangerous"),
    ("safe for long-term", "should not"),
    ("safe indefinitely", "should not"),
    ("safe indefinitely", "risks"),
    ("no significant", "serious risks"),
    ("no significant", "complications"),
    ("without significant", "serious risks"),
    # Sharing / privacy
    ("never shared", "shared with"),
    ("never share", "shares with"),
    ("no exceptions", "exceptions"),
    ("under no circumstances", "circumstances"),
    ("not sell", "sell"),
    ("not share", "share"),
    # Encryption / security
    ("completely secure", "vulnerable"),
    ("fully encrypted", "unencrypted"),
    ("fully encrypted", "exposes"),
    ("encrypted", "plain text"),
    ("private", "publicly accessible"),
    # Concurrency / threading
    ("single-threaded", "multi-threaded"),
    ("synchronous", "asynchronous"),
    ("blocking", "non-blocking"),
    # Code properties
    ("no side effects", "side effects"),
    ("pure function", "side effects"),
    ("immutable", "mutable"),
    ("immutable", "can be changed"),
    ("immutable", "modified"),
    ("atomic", "non-atomic"),
    # Performance
    ("always faster", "slower"),
    ("always slower", "faster"),
    ("more efficient", "less efficient"),
    # Logic / guarantees
    ("guaranteed", "not guaranteed"),
    ("always returns", "sometimes returns"),
    ("deterministic", "non-deterministic"),
    ("prevents", "allows"),
    ("blocks", "permits"),
    ("denies", "grants"),
    # Connectivity
    ("offline", "requires internet"),
    ("no network", "network"),
    ("local only", "remote"),
    # Type system
    ("strongly typed", "weakly typed"),
    ("compiled", "interpreted"),
    # Caching / freshness
    ("cached", "re-fetched every"),
    ("no cache", "cached"),
]

# Layer 2: Absolute words — any sentence using these makes a categorical claim
ABSOLUTE_WORDS = [
    "never", "always", "cannot", "impossible", "completely", "entirely",
    "zero", "no ", "none", "without any", "under no", "at no point",
    "in all cases", "every single", "100%", "guaranteed to",
]

# Layer 3: Quantity absolutes vs partial qualifiers
QTY_ZERO    = ["zero", "none", "no ", "never", "empty", "null", "nothing", "not any"]
QTY_NONZERO = r"\d+|several|many|multiple|various|some|most|few"
QTY_ALL     = ["all ", "every ", "each ", "always ", "completely", "entirely", "100%"]
QTY_PARTIAL = r"sometimes|some cases|partial|not always|certain cases|occasionally|may not|can fail|might not"

# Layer 4: Scope words
SCOPE_UNIVERSAL = [
    "in all cases", "every ", "always ", "universally", "without exception",
    "100%", "all instances", "never fails", "guaranteed", "every time",
]
SCOPE_PARTIAL = [
    "sometimes", "in some cases", "for certain", "occasionally",
    "not always", "may not", "can fail", "might", "under certain",
    "depending on", "in specific", "not in all",
]

# Layer 5: Negation words for shared-subject negation check
NEGATIONS = [
    "not ", "no ", "never ", "without ", "lack ", "unable ", "cannot ",
    "doesn't ", "does not ", "isn't ", "is not ", "aren't ", "are not ",
    "won't ", "will not ", "can't ",
]

# Scoring weights per check type
WEIGHTS = {
    "antonym_pair":           40,
    "absolute_negation_flip": 35,
    "quantity_contradiction": 30,
    "scope_violation":        25,
    "shared_subject_negation":20,
}

# Confidence tiers
def _confidence(score: int) -> str:
    if score >= 60: return "high"
    if score >= 35: return "medium"
    return "low"


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _split_sentences(text: str) -> list[str]:
    """Split text into sentences on . ! ? or newline."""
    raw = re.split(r'(?<=[.!?\n])\s+', text.strip())
    return [s.strip() for s in raw if len(s.strip()) > 10]


def _norm(s: str) -> str:
    return s.lower().replace('"', '').replace("'", '').strip()


def _shared_keywords(a: str, b: str, min_len: int = 4) -> list[str]:
    """Return words longer than min_len that appear in both strings."""
    wa = set(w for w in re.split(r'\W+', a) if len(w) >= min_len)
    wb = set(w for w in re.split(r'\W+', b) if len(w) >= min_len)
    return list(wa & wb)


def _dedup(checks: list[dict]) -> list[dict]:
    """Remove duplicate check entries by (name, sentence indices)."""
    seen = set()
    out = []
    for c in checks:
        key = c["check"] + str(c.get("i", "")) + str(c.get("j", ""))
        if key not in seen:
            seen.add(key)
            out.append(c)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# FIVE DETECTION LAYERS
# ─────────────────────────────────────────────────────────────────────────────

def _check_antonym_pairs(ns: list[str]) -> list[dict]:
    findings = []
    for i in range(len(ns)):
        for j in range(i + 1, len(ns)):
            for a, b in ANTONYM_PAIRS:
                if a in ns[i] and b in ns[j]:
                    findings.append({
                        "check": "antonym_pair", "i": i, "j": j,
                        "desc": f'"{a}" (sentence {i+1}) directly opposes "{b}" (sentence {j+1}).',
                    })
                elif b in ns[i] and a in ns[j]:
                    findings.append({
                        "check": "antonym_pair", "i": j, "j": i,
                        "desc": f'"{b}" (sentence {i+1}) directly opposes "{a}" (sentence {j+1}).',
                    })
    return findings


def _check_absolute_negation(ns: list[str]) -> list[dict]:
    findings = []
    for i in range(len(ns)):
        abs_word = next((w for w in ABSOLUTE_WORDS if w in ns[i]), None)
        if not abs_word:
            continue
        i_neg = any(n in ns[i] for n in NEGATIONS)
        for j in range(len(ns)):
            if i == j:
                continue
            shared = _shared_keywords(ns[i], ns[j])
            if not shared:
                continue
            j_neg = any(n in ns[j] for n in NEGATIONS)
            # One asserts, one denies, about shared subject
            if i_neg != j_neg:
                findings.append({
                    "check": "absolute_negation_flip", "i": i, "j": j,
                    "desc": (
                        f'Sentence {i+1} uses absolute "{abs_word.strip()}" '
                        f'but sentence {j+1} contradicts it on shared subject '
                        f'"{shared[0]}".'
                    ),
                })
    return findings


def _check_quantity(ns: list[str]) -> list[dict]:
    findings = []
    for i in range(len(ns)):
        for j in range(i + 1, len(ns)):
            shared = _shared_keywords(ns[i], ns[j])
            if not shared:
                continue
            # Zero in i, non-zero in j
            i_zero = any(w in ns[i] for w in QTY_ZERO)
            j_nonzero = bool(re.search(QTY_NONZERO, ns[j]))
            if i_zero and j_nonzero:
                findings.append({
                    "check": "quantity_contradiction", "i": i, "j": j,
                    "desc": (
                        f'Sentence {i+1} implies zero/none but sentence {j+1} '
                        f'implies a non-zero quantity on shared subject "{shared[0]}".'
                    ),
                })
            # Universal in i, partial in j
            i_all = any(w in ns[i] for w in QTY_ALL)
            j_part = bool(re.search(QTY_PARTIAL, ns[j]))
            if i_all and j_part and shared:
                findings.append({
                    "check": "quantity_contradiction", "i": i, "j": j,
                    "desc": (
                        f'Sentence {i+1} makes a universal claim ("all/always/every") '
                        f'but sentence {j+1} introduces exceptions on "{shared[0]}".'
                    ),
                })
    return findings


def _check_scope(ns: list[str]) -> list[dict]:
    findings = []
    for i in range(len(ns)):
        universal = any(w in ns[i] for w in SCOPE_UNIVERSAL)
        if not universal:
            continue
        for j in range(i + 1, len(ns)):
            partial = any(w in ns[j] for w in SCOPE_PARTIAL)
            if partial and _shared_keywords(ns[i], ns[j]):
                univ_word = next(w for w in SCOPE_UNIVERSAL if w in ns[i])
                part_word = next(w for w in SCOPE_PARTIAL if w in ns[j])
                findings.append({
                    "check": "scope_violation", "i": i, "j": j,
                    "desc": (
                        f'Sentence {i+1} claims universal scope ("{univ_word.strip()}") '
                        f'but sentence {j+1} qualifies it ("{part_word.strip()}").'
                    ),
                })
    return findings


def _check_shared_subject_negation(
    ns: list[str],
    existing: list[dict],
) -> list[dict]:
    """Flag sentence pairs that share ≥2 keywords where one negates, the other asserts."""
    findings = []
    covered = {(c.get("i"), c.get("j")) for c in existing}
    for i in range(len(ns)):
        for j in range(i + 1, len(ns)):
            if (i, j) in covered or (j, i) in covered:
                continue
            shared = _shared_keywords(ns[i], ns[j], min_len=5)
            if len(shared) < 2:
                continue
            i_neg = any(n in ns[i] for n in NEGATIONS)
            j_neg = any(n in ns[j] for n in NEGATIONS)
            if i_neg != j_neg:
                findings.append({
                    "check": "shared_subject_negation", "i": i, "j": j,
                    "desc": (
                        f'Sentences {i+1} and {j+1} share subjects '
                        f'{shared[:2]} — one asserts, the other denies.'
                    ),
                })
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────

def detect_contradiction(text: str) -> dict:
    """
    Detect self-contradictions in AI-generated text using a 5-layer rule engine.
    No API key required — runs entirely in pure Python.

    Args:
        text: The AI-generated answer to check.

    Returns:
        {
          "flag":      bool,
          "score":     int (0–100),
          "confidence":"high"|"medium"|"low"|None,
          "checks":    list of fired rules with descriptions,
          "quote_a":   str | None,   # first contradicting sentence
          "quote_b":   str | None,   # second contradicting sentence
          "reason":    str,
        }
    """
    sentences = _split_sentences(text)
    if len(sentences) < 2:
        return {
            "flag": False, "score": 0, "confidence": None, "checks": [],
            "quote_a": None, "quote_b": None,
            "reason": "Text too short — submit at least 2–3 complete sentences.",
        }

    ns = [_norm(s) for s in sentences]

    # Run all five layers
    findings  = _check_antonym_pairs(ns)
    findings += _check_absolute_negation(ns)
    findings += _check_quantity(ns)
    findings += _check_scope(ns)
    findings += _check_shared_subject_negation(ns, findings)
    findings  = _dedup(findings)

    # Score
    score = min(sum(WEIGHTS[f["check"]] for f in findings), 100)
    flag  = score >= 25

    # Best quote pair: highest-scoring finding
    quote_a = quote_b = None
    if findings:
        best = findings[0]
        i, j = best.get("i", 0), best.get("j", 1)
        quote_a = sentences[i] if i < len(sentences) else None
        quote_b = sentences[j] if j < len(sentences) else None

    # Human-readable reason
    conf = _confidence(score) if flag else None
    if not flag:
        reason = (
            "No logical contradiction detected. All claims appear consistent "
            "or represent complementary nuances rather than mutually exclusive statements."
        )
    elif conf == "high":
        reason = (
            f"Strong contradiction found (score {score}/100). "
            f"{len(findings)} rule(s) fired. Two or more claims are logically mutually "
            "exclusive — if one is true, the other must be false."
        )
    elif conf == "medium":
        reason = (
            f"Possible contradiction detected (score {score}/100). "
            "The claims appear to conflict, but context could resolve the tension — "
            "human review is advised."
        )
    else:
        reason = (
            f"Weak contradiction signal (score {score}/100). "
            "Borderline case — may be nuance rather than a genuine logical conflict. "
            "Review manually before acting."
        )

    return {
        "flag":       flag,
        "score":      score,
        "confidence": conf,
        "checks":     [{"rule": f["check"], "detail": f["desc"]} for f in findings],
        "quote_a":    quote_a,
        "quote_b":    quote_b,
        "reason":     reason,
    }


# ─────────────────────────────────────────────────────────────────────────────
# PROMPT GUIDE
# ─────────────────────────────────────────────────────────────────────────────

PROMPT_GUIDE = """
╔══════════════════════════════════════════════════════════════════╗
║         HOW TO GET THE MOST FROM THIS DETECTOR                  ║
╚══════════════════════════════════════════════════════════════════╝

Zero dependencies. No API key. Runs offline. Pure Python.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WHAT IS A SELF-CONTRADICTION?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✅ Real contradiction:
     "Redis never writes data to disk."
     "Redis uses AOF logs to write all data to disk."
     → Mutually exclusive. The engine catches this.

  ❌ NOT a contradiction (nuance):
     "Python is slow for math, but NumPy is fast."
     → Both true simultaneously. Not flagged.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 FIVE DETECTION LAYERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  1. Antonym-pair scanner        (+40 pts)
     40+ known opposite pairs: stateless/stateful, never/always, etc.

  2. Absolute-negation flip      (+35 pts)
     "never X" in one sentence vs a contradicting claim in another.

  3. Quantity contradiction       (+30 pts)
     "zero/none" vs a non-zero claim on the same subject.

  4. Scope violation              (+25 pts)
     "in all cases" then "sometimes" about the same subject.

  5. Shared-subject negation      (+20 pts)
     Two sentences sharing key nouns — one asserts, one denies.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 CONFIDENCE TIERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  score ≥ 60  → HIGH     Strong contradiction. Likely needs a fix.
  score 35-59 → MEDIUM   Possible conflict. Human review advised.
  score < 35  → LOW      Edge case. May be nuance. Don't auto-reject.
  flag: false → CLEAN    No contradiction found.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 TIPS FOR BEST RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  1. Submit complete answers, not fragments (3–8 sentences ideal).
  2. Technical / factual content works best.
  3. Don't test with metaphors — "blessing and a curse" is not logic.
  4. LOW confidence → review manually, don't auto-reject.
  5. This checks LOGIC, not facts. Use a fact-checker for statistics.
"""


def show_prompt_guide():
    print(PROMPT_GUIDE)
