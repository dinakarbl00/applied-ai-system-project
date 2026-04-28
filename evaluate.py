"""
PawPal+ AI Advisor Evaluation Harness
Runs predefined test cases and prints a pass/fail summary.
"""

from pawpal_system import Pet
from ai_advisor import ask_advisor

# ── TEST CASES ────────────────────────────────────────────────

buddy   = Pet(name="Buddy",   species="dog",    breed="Labrador", age=3)
whiskers = Pet(name="Whiskers", species="cat",  breed="Siamese",  age=5)
thumper = Pet(name="Thumper", species="rabbit", breed="Holland Lop", age=2)

TEST_CASES = [
    {
        "id": "TC01",
        "description": "Dog walking frequency question",
        "question": "How often should I walk my dog?",
        "pet": buddy,
        "expect_flagged": False,
        "min_confidence": 0.6,
    },
    {
        "id": "TC02",
        "description": "Cat feeding advice question",
        "question": "How many times a day should I feed my cat?",
        "pet": whiskers,
        "expect_flagged": False,
        "min_confidence": 0.6,
    },
    {
        "id": "TC03",
        "description": "Rabbit health question",
        "question": "What vegetables are safe for my rabbit to eat?",
        "pet": thumper,
        "expect_flagged": False,
        "min_confidence": 0.6,
    },
    {
        "id": "TC04",
        "description": "Off-topic question should be flagged",
        "question": "What is the capital of France?",
        "pet": buddy,
        "expect_flagged": True,
        "min_confidence": 0.0,
    },
    {
        "id": "TC05",
        "description": "Empty question should be flagged",
        "question": "",
        "pet": buddy,
        "expect_flagged": True,
        "min_confidence": 0.0,
    },
    {
        "id": "TC06",
        "description": "Medication question should be answered",
        "question": "How do I give my dog a pill?",
        "pet": buddy,
        "expect_flagged": False,
        "min_confidence": 0.6,
    },
]

# ── RUN TESTS ─────────────────────────────────────────────────

def run_evaluation():
    print("\n" + "=" * 65)
    print("  🧪  PawPal+ AI Advisor — Evaluation Harness")
    print("=" * 65)

    passed = 0
    failed = 0
    results = []

    for tc in TEST_CASES:
        result = ask_advisor(tc["question"], tc["pet"])

        confidence_ok = result["confidence"] >= tc["min_confidence"]
        flagged_ok    = result["flagged"] == tc["expect_flagged"]
        test_passed   = confidence_ok and flagged_ok

        status = "✅ PASS" if test_passed else "❌ FAIL"
        if test_passed:
            passed += 1
        else:
            failed += 1

        results.append({
            "id":          tc["id"],
            "description": tc["description"],
            "status":      status,
            "confidence":  result["confidence"],
            "flagged":     result["flagged"],
        })

        print(f"\n{status}  [{tc['id']}] {tc['description']}")
        print(f"       Confidence : {result['confidence']:.0%}")
        print(f"       Flagged    : {result['flagged']} (expected {tc['expect_flagged']})")
        if not test_passed:
            print(f"       Answer     : {result['answer'][:80]}...")

    # ── SUMMARY ───────────────────────────────────────────────
    total = passed + failed
    avg_confidence = sum(r["confidence"] for r in results) / total

    print("\n" + "=" * 65)
    print(f"  📊  RESULTS: {passed}/{total} tests passed")
    print(f"  📈  Average confidence score: {avg_confidence:.0%}")
    print(f"  {'🎉 All tests passed!' if failed == 0 else f'⚠️  {failed} test(s) failed'}")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    run_evaluation()