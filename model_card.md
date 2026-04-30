# Model Card: PawPal+ AI Care Advisor

## 1. Model Name
**PawPal+ AI Care Advisor**

---

## 2. Base Project
This builds on PawPal+, a pet care scheduling app I built in Module 2. The
original version was purely algorithmic, it handled task scheduling, priority
sorting, and conflict detection, but had no AI in it at all. For this version
I wanted to answer a question the original couldn't: what should I actually
do for my pet, not just when to do it.

---

## 3. AI Feature Added
When a user asks a question like "how often should I walk my dog?", the advisor
pulls that pet's profile: name, species, breed, age, and current tasks, and
sends it to Gemini along with the question. The model returns a personalized
answer rather than a generic one. Every response ends with a confidence score
that the application uses to decide whether to flag the answer as low quality
or off-topic.

---

## 4. Intended Use
- Helping busy pet owners get quick, personalized care advice
- Demonstrating how a language model can be integrated into a real working app
- Not a replacement for a vet, emergency or medical questions should always
  go to a professional

---

## 5. Limitations and Bias
The biggest limitation is that the confidence score comes from the model itself,
which means it is not truly calibrated. Gemini tends to say 95% on almost
everything it answers, which makes it hard to distinguish a very good answer
from an okay one. There is also no memory between questions, every call starts
fresh, so the model does not know what you asked two minutes ago. And like any
general-purpose model, the advice is broad. A Labrador and a Chihuahua might
get similar answers even though their needs are quite different.

---

## 6. Evaluation Results

| Test | Description | Result | Confidence |
|------|-------------|--------|------------|
| TC01 | Dog walking frequency | PASS | 95% |
| TC02 | Cat feeding advice | PASS | 95% |
| TC03 | Rabbit safe vegetables | PASS | 100% |
| TC04 | Off-topic question (guardrail) | PASS | 0% |
| TC05 | Empty input (guardrail) | PASS | 0% |
| TC06 | Medication administration | PASS | 95% |

6 out of 6 tests passed. The average confidence across all inputs was 64%,
which looks low but makes sense, the two guardrail tests score 0% by design.
On legitimate pet care questions alone the average was 96%.

---

## 7. AI Collaboration Reflection

### How I used AI during this project
I used Claude throughout the project, for designing the architecture, writing the advisor
module, structuring the evaluation harness, and debugging the Gemini API issues
that came up along the way. It was more like pair programming than just asking
questions.

### One helpful suggestion
Claude recommended keeping the AI advisor in its own file rather than folding
it into the core system. That turned out to be the right call. The scheduling
logic stayed clean and independent, and the app still runs fully without an API
key. It is a small thing but it made the codebase much easier to reason about.

### One flawed suggestion
Claude told me to use the `google.generativeai` package and `gemini-1.5-flash`
as the model. Both were wrong, the library was deprecated and the model was
not available on my account. It took several rounds of trial and error, trying
different model names and libraries, before landing on `google-genai` and
`gemini-2.5-flash`. The AI was confidently wrong, which was a good reminder
to always verify suggestions against actual documentation.

### What surprised me during testing
I expected the guardrail to be fragile, that the model would try to answer
off-topic questions anyway or give a vague pet-related spin to something
unrelated. It did not. It flatly said it could only help with pet care questions
and returned 0% confidence, exactly as instructed. What surprised me on the
other side was how consistently high the confidence scores were on legitimate
questions. 95% every time starts to feel less like a measurement and more like
a default. That is something I would want to fix in a real version of this.

---

## 8. Future Improvements
The most useful next step would be grounding the answers in actual veterinary
sources using retrieval-augmented generation, right now the model is drawing
on its training data, which may be outdated or too general. I would also want
to add conversation memory so follow-up questions have context, and replace the
self-reported confidence score with something more reliable, like a second model
checking the first one's answer.