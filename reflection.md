# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
- A:    I designed four classes for this scenario. 
Task: this is responsible for the details about the work, such as description, due time, due date, frequency, priority, completed and task type.
Pet: this is responsible for the pet's identity, such as name, species, breed and age. It also has a list of Task objects.
Owner: this is the top-level data store. It holds pets and provides get_all_tasks(), which flattens every pet's tasks into one flat list of (pet_name, Task) tuples. This single method is the only way the Scheduler reads data, which keeps the two classes loosely coupled.
Scheduler: this is more of a business logic. The Scheduler holds no data; it only reads from Owner and returns results. This makes it easy to test and extend.

Core action for users:
1. Add a pet with identifying information (name, species, breed, age)
2. Schedule a care task for a pet (description, time, date, frequency, priority)
3. View today's schedule sorted and filtered in a useful, prioritised way

**b. Design changes**

- Did your design change during implementation?
- A: Yes
- If yes, describe at least one change and why you made it.
- A: Added task_id to Task class. This was because I needed a way to uniquely identify tasks for editing and deleting, and the combination of description and due time was not guaranteed to be unique. Adding a task_id made it easier to manage tasks without relying on potentially ambiguous attributes.
I will be using explicit list type hints instead of generic list returns. This is because it provides more clarity on what type of data is being returned, which can help with debugging and understanding the code.
I accepted these changes while I rejected Date/time as string fields. Copilot suggested parsing `due_time` and `due_date` into proper datetime objects
at creation time. I rejected this because zero-padded HH:MM strings sort correctly
using plain string comparison, and adding `__post_init__` validation would increase
complexity without meaningful benefit at this project's scale.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- A: The scheduler considers time, date, priority level, and task type.
- How did you decide which constraints mattered most?
- A: Priority was chosen as the primary sort key over time because a high-priority
vet appointment at 14:00 is more important to surface than a low-priority
walk at 07:00. Time acts as a tiebreaker within each priority band.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- A: Conflict detection uses exact time matching, not duration-based overlap.
Two tasks are only flagged as conflicting if they share the exact same. A walk at 08:00 and a grooming at 08:15 would not be flagged even if the walk takes 45 minutes. 
- Why is that tradeoff reasonable for this scenario?
- A: This is reasonable here because most pet care tasks are instant events rather than extended blocks. Asking users to estimate duration for every task adds friction for little gain. The most
common real mistake of double-booking the exact same slot is fully caught.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
