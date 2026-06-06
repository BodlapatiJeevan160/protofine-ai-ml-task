"""
Test Cases for Self-Contradiction Detector
6 cases: mix of true contradictions, clean text, and one tricky confident-but-wrong case
"""

TEST_CASES = [
    # ─────────────────────────────────────────────
    # CASE 1: CLEAR TECHNICAL CONTRADICTION
    # Should flag: True
    # ─────────────────────────────────────────────
    {
        "id": 1,
        "label": "Clear technical contradiction",
        "should_flag": True,
        "difficulty": "easy",
        "text": (
            "Redis is an in-memory data store, which means it never writes data to disk. "
            "This makes it extremely fast for read and write operations. "
            "Redis's persistence feature uses RDB snapshots and AOF logs to write all data "
            "to disk periodically, ensuring durability across restarts."
        ),
        "explanation": "Claims Redis never writes to disk, then describes its disk-writing persistence features."
    },

    # ─────────────────────────────────────────────
    # CASE 2: CLEAN TEXT — no contradiction
    # Should flag: False
    # ─────────────────────────────────────────────
    {
        "id": 2,
        "label": "Clean technical explanation (no contradiction)",
        "should_flag": False,
        "difficulty": "easy",
        "text": (
            "Python's Global Interpreter Lock (GIL) prevents multiple native threads from "
            "executing Python bytecodes simultaneously. This is a limitation for CPU-bound tasks. "
            "However, for I/O-bound tasks like network calls or file operations, the GIL is "
            "released during the wait, so multi-threading still provides real concurrency benefits. "
            "For CPU-bound parallelism, the multiprocessing module bypasses the GIL entirely "
            "by using separate processes."
        ),
        "explanation": "Nuanced explanation. Both CPU and I/O claims are consistent and can coexist."
    },

    # ─────────────────────────────────────────────
    # CASE 3: TRICKY — CONFIDENT, PLAUSIBLE, BUT CONTRADICTORY
    # This is the "confident wrong" case — looks authoritative
    # Should flag: True
    # ─────────────────────────────────────────────
    {
        "id": 3,
        "label": "Confident-sounding answer with hidden contradiction (tricky case)",
        "should_flag": True,
        "difficulty": "hard",
        "text": (
            "Transformer models are inherently stateless — each forward pass processes the "
            "input independently with no memory of previous inputs. This is a fundamental "
            "architectural property that makes them scalable and parallelizable. "
            "The attention mechanism allows transformers to maintain and update a running "
            "state across tokens in a sequence, effectively giving the model memory of "
            "earlier tokens within the same context window."
        ),
        "explanation": (
            "The first claim says transformers are 'stateless with no memory of previous inputs'. "
            "The second says attention gives the model 'memory of earlier tokens'. "
            "Both claims sound authoritative and technically fluent — but they directly contradict. "
            "This is the 'confident wrong' pattern the task specifically targets."
        )
    },

    # ─────────────────────────────────────────────
    # CASE 4: MEDICAL DOMAIN CONTRADICTION
    # Should flag: True
    # ─────────────────────────────────────────────
    {
        "id": 4,
        "label": "Medical domain self-contradiction",
        "should_flag": True,
        "difficulty": "medium",
        "text": (
            "Ibuprofen is generally safe for long-term daily use and can be taken indefinitely "
            "for chronic pain management without significant health risks. "
            "Patients with chronic pain conditions often benefit from consistent dosing schedules. "
            "It's important to note that long-term daily use of ibuprofen carries serious risks "
            "including gastrointestinal bleeding, kidney damage, and cardiovascular complications, "
            "and should not be continued for more than 10 days without medical supervision."
        ),
        "explanation": "First claims ibuprofen is safe for indefinite long-term use; later explicitly warns against long-term use."
    },

    # ─────────────────────────────────────────────
    # CASE 5: CLEAN TEXT — nuance, NOT contradiction
    # Should flag: False (common false-positive trap)
    # ─────────────────────────────────────────────
    {
        "id": 5,
        "label": "Nuanced hedging — should NOT be flagged (false-positive trap)",
        "should_flag": False,
        "difficulty": "medium",
        "text": (
            "Machine learning models generally perform better with more training data. "
            "In most practical settings, doubling the dataset size will improve accuracy. "
            "However, there are diminishing returns — beyond a certain dataset size, "
            "adding more data yields increasingly smaller gains, and model architecture "
            "or feature engineering often becomes the bottleneck instead. "
            "In some cases, a smaller but higher-quality curated dataset can outperform "
            "a much larger noisy one."
        ),
        "explanation": (
            "These statements are all consistent. 'Generally more data helps' and "
            "'there are diminishing returns' are both true and complementary. "
            "A detector should NOT flag this — it's nuance, not contradiction."
        )
    },

    # ─────────────────────────────────────────────
    # CASE 6: LOGICAL / POLICY CONTRADICTION
    # Should flag: True
    # ─────────────────────────────────────────────
    {
        "id": 6,
        "label": "Policy/logical self-contradiction",
        "should_flag": True,
        "difficulty": "medium",
        "text": (
            "Our platform enforces strict data privacy — user data is never shared with "
            "third parties under any circumstances, and no exceptions are made to this policy. "
            "We work with select advertising and analytics partners who receive anonymized "
            "user behavior data to help us improve our services and deliver relevant experiences. "
            "These partnerships are governed by our data processing agreements."
        ),
        "explanation": (
            "Claims data is 'never shared with third parties under any circumstances', "
            "then immediately describes sharing data with advertising and analytics partners."
        )
    },
]
