"""
Test Runner — Self-Contradiction Detector
Runs all 6 cases and reports precision / recall / F1.
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detector import detect_contradiction
from test_cases import TEST_CASES


def run_tests():
    passed = failed = 0
    results = []

    print("\n" + "═" * 62)
    print("   CONTRADICTION DETECTOR — TEST SUITE  (no API required)")
    print("═" * 62)

    for case in TEST_CASES:
        print(f"\n▸ Case {case['id']}: {case['label']}")
        print(f"  Difficulty : {case['difficulty']}")
        print(f"  Expected   : {'⚠ SHOULD FLAG' if case['should_flag'] else '✓ SHOULD PASS'}")

        result = detect_contradiction(case["text"])
        flagged = result["flag"]
        correct = (flagged == case["should_flag"])

        if correct: passed += 1
        else:       failed += 1

        status = "✅ PASS" if correct else "❌ FAIL"
        print(f"  Got        : {'⚠ FLAGGED' if flagged else '✓ CLEAN'}")
        print(f"  Score      : {result['score']}/100  confidence={result['confidence'] or 'n/a'}")
        print(f"  Status     : {status}")
        print(f"  Reason     : {result['reason']}")
        if flagged and result["checks"]:
            for c in result["checks"][:2]:
                print(f"  Rule       : [{c['rule']}] {c['detail']}")

        results.append({**case, "result": result, "detector_flagged": flagged, "passed": correct})

    # ── Metrics ──────────────────────────────────────────────
    tp = sum(1 for r in results if r["should_flag"]  and r["detector_flagged"])
    fp = sum(1 for r in results if not r["should_flag"] and r["detector_flagged"])
    fn = sum(1 for r in results if r["should_flag"]  and not r["detector_flagged"])
    tn = sum(1 for r in results if not r["should_flag"] and not r["detector_flagged"])

    prec = tp / (tp + fp) if (tp + fp) else 0
    rec  = tp / (tp + fn) if (tp + fn) else 0
    f1   = 2 * prec * rec / (prec + rec) if (prec + rec) else 0

    print("\n" + "═" * 62)
    print(f"   RESULTS : {passed}/{len(TEST_CASES)} passed   |   {failed} failed")
    print(f"   TP={tp}  FP={fp}  FN={fn}  TN={tn}")
    print(f"   Precision : {prec:.2f}   Recall : {rec:.2f}   F1 : {f1:.2f}")
    print("═" * 62)

    out = os.path.join(os.path.dirname(__file__), "test_results.json")
    with open(out, "w") as f:
        json.dump([{
            "id": r["id"], "label": r["label"],
            "should_flag": r["should_flag"],
            "detector_flagged": r["detector_flagged"],
            "score": r["result"]["score"],
            "confidence": r["result"]["confidence"],
            "passed": r["passed"],
        } for r in results], f, indent=2)
    print(f"\n  Results saved → {out}\n")
    return results


if __name__ == "__main__":
    run_tests()
