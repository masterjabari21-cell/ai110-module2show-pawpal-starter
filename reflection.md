# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Three core actions a user should be able to perform:

1. **Add a pet** — The user enters basic pet information (name, species, age, and any special needs) so the system knows who it is planning care for.
2. **Add and manage care tasks** — The user creates tasks such as a morning walk, feeding, medication, or grooming, each with a title, estimated duration in minutes, and a priority level (low, medium, or high).
3. **Generate and view today's schedule** — The user triggers the scheduler, which selects and orders tasks based on the owner's available time and task priorities, then displays the resulting daily plan with a plain-language explanation of why each task was included and when it happens.

The four main building blocks are:

- **Owner** — holds the owner's name, how many minutes they have available today, and any personal preferences (e.g., prefers morning tasks). Responsible for setting availability and owning one or more pets.
- **Pet** — holds pet info (name, species, age, special needs) and the list of care tasks associated with that pet.
- **Task** — a dataclass holding a task's title, duration in minutes, priority, and category. Knows whether it is high-priority.
- **Scheduler** — receives an Owner, a Pet, and the task list, then builds an ordered daily plan that fits within the available time. Also generates a human-readable explanation of the plan.

Relationships: an Owner owns one or more Pets; a Pet has zero or more Tasks; the Scheduler uses the Owner and Pet to produce a plan from the Task list.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
