"""
main.py — CLI entry point
Usage:
    python main.py                     # show prompt guide
    python main.py --check "text..."   # analyze a single text
    python main.py --test              # run full test suite
    python main.py --guide             # print the prompt guide
"""

import argparse
import json
import sys
from detector import detect_contradiction, show_prompt_guide


def main():
    parser = argparse.ArgumentParser(
        description="Self-Contradiction Detector — no API key required"
    )
    parser.add_argument("--check", type=str, help="Text to analyze")
    parser.add_argument("--test",  action="store_true", help="Run full test suite")
    parser.add_argument("--guide", action="store_true", help="Show prompt guide")
    args = parser.parse_args()

    if len(sys.argv) == 1 or args.guide:
        show_prompt_guide()
        return

    if args.test:
        from run_tests import run_tests
        run_tests()
        return

    if args.check:
        print("\nAnalyzing...\n")
        result = detect_contradiction(args.check)
        print(json.dumps(result, indent=2))
        print("\n" + "─" * 52)
        if result["flag"]:
            print(f"⚠  CONTRADICTION  [{(result['confidence'] or '').upper()} confidence]  score {result['score']}/100")
            print(f"   {result['reason']}")
            if result["quote_a"]:
                print(f"\n   Claim A: \"{result['quote_a']}\"")
                print(f"   Claim B: \"{result['quote_b']}\"")
            if result["checks"]:
                print("\n   Rules fired:")
                for c in result["checks"]:
                    print(f"     • [{c['rule']}] {c['detail']}")
        else:
            print(f"✓  CLEAN — {result['reason']}")
        print("─" * 52)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
