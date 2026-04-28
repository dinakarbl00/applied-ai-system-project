import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pawpal_system import Owner, Pet

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are PawPal+, a friendly and knowledgeable pet care assistant.
You give concise, practical advice based on the pet's profile provided.
Always personalize your answer using the pet's name, species, breed, and age.
End every response with a confidence score in this exact format:
CONFIDENCE: 0.XX
Where 0.00 is no confidence and 1.00 is complete confidence.
If the question is not about pet care, say you can only help with pet care questions
and give CONFIDENCE: 0.00"""


def ask_advisor(question: str, pet: Pet) -> dict:
    """
    Send a pet care question to Gemini with the pet's profile as context.
    Returns a dict with 'answer', 'confidence', and 'flagged' keys.
    """
    if not question or not question.strip():
        return {
            "answer": "Please ask a valid question.",
            "confidence": 0.0,
            "flagged": True
        }

    pet_context = f"""
Pet Profile:
- Name: {pet.name}
- Species: {pet.species}
- Breed: {pet.breed}
- Age: {pet.age} years old
- Current tasks: {[t.description for t in pet.get_pending_tasks()]}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            ),
            contents=f"{pet_context}\n\nQuestion: {question}"
        )

        full_response = response.text

        # Parse confidence score from response
        confidence = 0.5
        flagged = False
        lines = full_response.strip().split("\n")
        for line in lines:
            if line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.split(":")[1].strip())
                except ValueError:
                    confidence = 0.5

        # Remove the confidence line from the displayed answer
        answer_lines = [l for l in lines if not l.startswith("CONFIDENCE:")]
        answer = "\n".join(answer_lines).strip()

        # Guardrail: flag low confidence or off-topic responses
        if confidence < 0.4:
            flagged = True

        return {
            "answer": answer,
            "confidence": confidence,
            "flagged": flagged
        }

    except Exception as e:
        return {
            "answer": f"Error contacting AI advisor: {str(e)}",
            "confidence": 0.0,
            "flagged": True
        }


def demo_advisor(owner: Owner) -> None:
    """Run a quick CLI demo of the advisor with 3 sample questions."""
    if not owner.pets:
        print("No pets found. Add a pet first.")
        return

    questions = [
        ("How often should I walk my pet?", owner.pets[0]),
        ("What should I feed my pet and how many times a day?", owner.pets[0]),
        ("What is the capital of France?", owner.pets[0]),
    ]

    print("\n" + "=" * 60)
    print("  🤖  PawPal+ AI Care Advisor Demo")
    print("=" * 60)

    for question, pet in questions:
        print(f"\n📋 Pet: {pet.name} ({pet.breed}, {pet.age} yrs)")
        print(f"❓ Question: {question}")
        print("-" * 60)

        result = ask_advisor(question, pet)

        print(f"💬 Answer:\n{result['answer']}")
        print(f"\n📊 Confidence: {result['confidence']:.0%}")
        if result["flagged"]:
            print("⚠️  Guardrail triggered: low confidence or off-topic response")
        print("=" * 60)


if __name__ == "__main__":
    owner = Owner.load_from_json("data.json")
    if not owner:
        owner = Owner(name="Demo User")
        pet = Pet(name="Buddy", species="dog", breed="Labrador", age=3)
        owner.add_pet(pet)

    demo_advisor(owner)