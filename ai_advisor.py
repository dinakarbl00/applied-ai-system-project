import os
import time
from groq import Groq
from dotenv import load_dotenv
from pawpal_system import Owner, Pet

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are PawPal+, a friendly and knowledgeable pet care assistant.

You give concise, practical advice based on the pet's profile provided.

Always personalize your answer using the pet's name, species, breed, and age.

If the conversation history shows earlier questions about this pet, use that
context to give more relevant follow-up answers — but do not repeat advice
already given unless the user asks.

End every response with a confidence score in this exact format:
CONFIDENCE: 0.XX

Where 0.00 is no confidence and 1.00 is complete confidence.

If the question is not about pet care, say you can only help with pet care
questions and give CONFIDENCE: 0.00"""


def ask_advisor(question: str, pet: Pet, history: list = None) -> dict:
    """
    Send a pet care question to Groq LLM with the pet's profile and
    optional conversation history as context.

    Args:
        question: The user's question string.
        pet:      The Pet object whose profile is used as context.
        history:  List of prior turns, each a dict with keys
                  'role' ('user' or 'assistant') and 'text' (str).
                  Defaults to empty list (stateless, backward-compatible).

    Returns:
        dict with keys:
            'answer'     - cleaned response text (no CONFIDENCE line)
            'confidence' - float 0.0-1.0
            'flagged'    - bool, True if guardrail triggered
    """
    if history is None:
        history = []

    # Guard: empty question
    if not question or not question.strip():
        return {
            "answer": "Please ask a valid question.",
            "confidence": 0.0,
            "flagged": True,
        }

    # Build pet context block
    pet_context = (
        f"Pet Profile:\n"
        f"- Name: {pet.name}\n"
        f"- Species: {pet.species}\n"
        f"- Breed: {pet.breed}\n"
        f"- Age: {pet.age} years old\n"
        f"- Current tasks: {[t.description for t in pet.get_pending_tasks()]}\n"
    )

    # Build messages list (OpenAI-compatible format)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        # First user turn includes pet context
        first_text = f"{pet_context}\n\nQuestion: {history[0]['text']}"
        messages.append({"role": "user", "content": first_text})
        # Remaining history turns
        for turn in history[1:]:
            messages.append({
                "role": turn["role"],
                "content": turn["text"]
            })
        # Current question as latest user turn
        messages.append({"role": "user", "content": question})
    else:
        # Single-turn — backward-compatible with eval harness
        messages.append({
            "role": "user",
            "content": f"{pet_context}\n\nQuestion: {question}"
        })

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=512,
        )

        full_response = response.choices[0].message.content
        confidence = 0.5
        flagged = False

        lines = full_response.strip().split("\n")
        for line in lines:
            if line.strip().startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.split(":")[1].strip())
                except ValueError:
                    confidence = 0.5

        # Strip CONFIDENCE line from displayed answer
        answer_lines = [l for l in lines if not l.strip().startswith("CONFIDENCE:")]
        answer = "\n".join(answer_lines).strip()

        # Guardrail
        if confidence < 0.4:
            flagged = True

        return {
            "answer": answer,
            "confidence": confidence,
            "flagged": flagged,
        }

    except Exception as e:
        return {
            "answer": f"Error contacting AI advisor: {str(e)}",
            "confidence": 0.0,
            "flagged": True,
        }


def demo_advisor(owner: Owner) -> None:
    """Run a quick CLI demo showing conversation history in action."""
    if not owner.pets:
        print("No pets found. Add a pet first.")
        return

    pet = owner.pets[0]
    history = []

    questions = [
        "How often should I walk my dog?",
        "And what about feeding — how many times a day?",
        "What is the capital of France?",
    ]

    print("\n" + "=" * 60)
    print(" 🤖 PawPal+ AI Care Advisor Demo (with history)")
    print("=" * 60)

    for question in questions:
        print(f"\n📋 Pet: {pet.name} ({pet.breed}, {pet.age} yrs)")
        print(f"❓ Question: {question}")
        print("-" * 60)

        result = ask_advisor(question, pet, history=history)

        print(f"💬 Answer:\n{result['answer']}")
        print(f"\n📊 Confidence: {result['confidence']:.0%}")
        if result["flagged"]:
            print("⚠️  Guardrail triggered: low confidence or off-topic")
        print("=" * 60)

        # Only add non-flagged turns to history
        if not result["flagged"]:
            history.append({"role": "user", "text": question})
            history.append({"role": "assistant", "text": result["answer"]})


if __name__ == "__main__":
    owner = Owner.load_from_json("data.json")
    if not owner:
        owner = Owner(name="Demo User")
        pet = Pet(name="Buddy", species="dog", breed="Labrador", age=3)
        owner.add_pet(pet)
    demo_advisor(owner)