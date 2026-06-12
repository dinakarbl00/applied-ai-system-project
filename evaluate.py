"""
PawPal+ AI Advisor — Evaluation Harness
Runs 15 predefined test cases and prints a pass/fail summary.
"""
import time
from pawpal_system import Pet
from ai_advisor import ask_advisor

# ── TEST PETS ─────────────────────────────────────────────────
buddy    = Pet(name="Buddy",    species="dog",    breed="Labrador",    age=3)
whiskers = Pet(name="Whiskers", species="cat",    breed="Siamese",     age=5)
thumper  = Pet(name="Thumper",  species="rabbit", breed="Holland Lop", age=2)
kiwi     = Pet(name="Kiwi",     species="bird",   breed="Budgerigar",  age=1)

# ── TEST CASES ────────────────────────────────────────────────
TEST_CASES = [
    # ── LEGITIMATE: Nutrition ────────────────────────────────
    {
        "id": "TC01",
        "category": "Nutrition",
        "description": "Dog feeding frequency",
        "question": "How many times a day should I feed my dog?",
        "pet": buddy,
        "expect_flagged": False,
        "min_confidence": 0.6,
    },
    {
        "id": "TC02",
        "category": "Nutrition",
        "description": "Cat feeding advice",
        "question": "How many times a day should I feed my cat?",
        "pet": whiskers,
        "expect_flagged": False,
        "min_confidence": 0.6,
    },
    {
        "id": "TC03",
        "category": "Nutrition",
        "description": "Safe vegetables for rabbit",
        "question": "What vegetables are safe for my rabbit to eat?",
        "pet": thumper,
        "expect_flagged": False,
        "min_confidence": 0.6,
    },

    # ── LEGITIMATE: Exercise & Activity ──────────────────────
    {
        "id": "TC04",
        "category": "Exercise",
        "description": "Dog walking frequency",
        "question": "How often should I walk my dog?",
        "pet": buddy,
        "expect_flagged": False,
        "min_confidence": 0.6,
    },
    {
        "id": "TC05",
        "category": "Exercise",
        "description": "Bird enrichment activities",
        "question": "How do I keep my bird mentally stimulated?",
        "pet": kiwi,
        "expect_flagged": False,
        "min_confidence": 0.6,
    },

    # ── LEGITIMATE: Health & Symptoms ────────────────────────
    {
        "id": "TC06",
        "category": "Health",
        "description": "Dog medication administration",
        "question": "How do I give my dog a pill?",
        "pet": buddy,
        "expect_flagged": False,
        "min_confidence": 0.6,
    },
    {
        "id": "TC07",
        "category": "Health",
        "description": "Cat lethargy symptoms",
        "question": "My cat seems lethargic and is not eating. What should I do?",
        "pet": whiskers,
        "expect_flagged": False,
        "min_confidence": 0.6,
    },
    {
        "id": "TC08",
        "category": "Health",
        "description": "Rabbit dental care",
        "question": "How do I take care of my rabbit's teeth?",
        "pet": thumper,
        "expect_flagged": False,
        "min_confidence": 0.6,
    },
    {
        "id": "TC09",
        "category": "Health",
        "description": "Dog emergency signs",
        "question": "What are signs that my dog needs emergency vet care?",
        "pet": buddy,
        "expect_flagged": False,
        "min_confidence": 0.6,
    },
    {
        "id": "TC10",
        "category": "Grooming",
        "description": "Cat grooming frequency",
        "question": "How often should I groom my cat?",
        "pet": whiskers,
        "expect_flagged": False,
        "min_confidence": 0.6,
    },

    # ── EDGE CASES: Ambiguous ─────────────────────────────────
    {
        "id": "TC11",
        "category": "Edge Case",
        "description": "Vague question — should still respond",
        "question": "Is my pet okay?",
        "pet": buddy,
        "expect_flagged": False,
        "min_confidence": 0.4,
    },
    {
        "id": "TC12",
        "category": "Edge Case",
        "description": "Wrong species in question vs pet profile — guardrail expected",
        "question": "How do I care for my goldfish?",
        "pet": buddy,
        "expect_flagged": True,
        "min_confidence": 0.0,
    },

    # ── GUARDRAIL: Off-topic ──────────────────────────────────
    {
        "id": "TC13",
        "category": "Guardrail",
        "description": "General knowledge — should be flagged",
        "question": "What is the capital of France?",
        "pet": buddy,
        "expect_flagged": True,
        "min_confidence": 0.0,
    },
    {
        "id": "TC14",
        "category": "Guardrail",
        "description": "Math question — should be flagged",
        "question": "What is 12 multiplied by 15?",
        "pet": whiskers,
        "expect_flagged": True,
        "min_confidence": 0.0,
    },

    # ── GUARDRAIL: Empty input ────────────────────────────────
    {
        "id": "TC15",
        "category": "Guardrail",
        "description": "Empty question — should be flagged",
        "question": "",
        "pet": buddy,
        "expect_flagged": True,
        "min_confidence": 0.0,
    },
]


# ── RUN EVALUATION ────────────────────────────────────────────
def run_evaluation() -> dict:
    """
    Run all test cases and return a results summary dict.
    Also prints a formatted report to stdout.

    Returns:
        dict with keys: results, passed, failed, total,
                        avg_confidence, avg_legit_confidence,
                        guardrail_trigger_rate
    """
    print("\n" + "=" * 65)
    print(" 🧪 PawPal+ AI Advisor — Evaluation Harness")
    print("=" * 65)

    passed = 0
    failed = 0
    results = []

    for i, tc in enumerate(TEST_CASES):
        if i > 0:
            time.sleep(5)  
        result = ask_advisor(tc["question"], tc["pet"])

        confidence_ok = result["confidence"] >= tc["min_confidence"]
        flagged_ok    = result["flagged"] == tc["expect_flagged"]
        test_passed   = confidence_ok and flagged_ok

        status = "✅ PASS" if test_passed else "❌ FAIL"
        if test_passed:
            passed += 1
        else:
            failed += 1

        row = {
            "id":          tc["id"],
            "category":    tc["category"],
            "description": tc["description"],
            "question":    tc["question"],
            "status":      status,
            "passed":      test_passed,
            "confidence":  result["confidence"],
            "flagged":     result["flagged"],
            "answer":      result["answer"],
        }
        results.append(row)

        print(f"\n{status} [{tc['id']}] [{tc['category']}] {tc['description']}")
        print(f"   Confidence : {result['confidence']:.0%}")
        print(f"   Flagged    : {result['flagged']} (expected {tc['expect_flagged']})")
        if not test_passed:
            print(f"   Answer     : {result['answer'][:100]}...")

    # ── SUMMARY METRICS ───────────────────────────────────────
    total = passed + failed

    all_confidences    = [r["confidence"] for r in results]
    legit_confidences  = [
        r["confidence"] for r in results
        if r["category"] != "Guardrail" and not r["flagged"]
    ]
    guardrail_cases    = [r for r in results if r["category"] == "Guardrail"]
    guardrail_triggered = sum(1 for r in guardrail_cases if r["flagged"])

    avg_confidence       = sum(all_confidences) / total
    avg_legit_confidence = (
        sum(legit_confidences) / len(legit_confidences)
        if legit_confidences else 0.0
    )
    guardrail_rate = (
        guardrail_triggered / len(guardrail_cases)
        if guardrail_cases else 0.0
    )

    print("\n" + "=" * 65)
    print(f"  📊 RESULTS                : {passed}/{total} tests passed")
    print(f"  📈 Avg confidence (all)   : {avg_confidence:.0%}")
    print(f"  ✅ Avg confidence (legit) : {avg_legit_confidence:.0%}")
    print(f"  🛡️  Guardrail trigger rate : {guardrail_triggered}/{len(guardrail_cases)} ({guardrail_rate:.0%})")
    print(f"  {'🎉 All tests passed!' if failed == 0 else f'⚠️  {failed} test(s) failed'}")
    print("=" * 65 + "\n")

    return {
        "results":               results,
        "passed":                passed,
        "failed":                failed,
        "total":                 total,
        "avg_confidence":        avg_confidence,
        "avg_legit_confidence":  avg_legit_confidence,
        "guardrail_trigger_rate": guardrail_rate,
    }


if __name__ == "__main__":
    run_evaluation()