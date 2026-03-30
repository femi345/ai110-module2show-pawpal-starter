# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The system is built around four classes.
`Task` is a Python dataclass that holds everything about a single care activity: its description, scheduled time in HH:MM format, duration in minutes, frequency (once/daily/weekly), priority level, completion flag, and due date.
`Pet` owns a list of `Task` objects and exposes methods to add, remove, and count them — it is the direct owner of task data.
`Owner` aggregates one or more `Pet` objects and provides a convenience method (`get_all_tasks`) that flattens all pet tasks into a single list of `(Pet, Task)` pairs.
`Scheduler` is the algorithmic brain: it holds a reference to the `Owner` and provides all sorting, filtering, conflict detection, and recurrence logic.
The `Scheduler` deliberately holds *no state of its own* beyond that reference, so it never goes out of sync with the underlying data.

The three core user actions identified before coding were:
1. Add a pet to the owner's household.
2. Schedule a care task for a specific pet (with time, duration, priority, and recurrence).
3. Generate and view today's sorted, conflict-checked schedule.

**b. Design changes**

The original sketch had conflict detection as a method on `Pet` (checking its own tasks).
During implementation it became clear that conflicts almost always occur *across* pets (e.g., a dog's morning walk and a cat's breakfast both at 07:30), so the method was moved to `Scheduler` where it can scan all `(Pet, Task)` pairs in one pass.
A second change was adding `sort_by_priority` as a first-class method alongside `sort_by_time`; the initial UML only had time-based sorting.
Finally, `mark_complete()` on `Task` was made to return a new `Task` rather than mutating in place for the recurrence case — this keeps the completed task as an immutable record while the follow-up becomes a separate, independently trackable object.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints: scheduled time (HH:MM), task priority (high/medium/low), and due date.
Time determines the default sort order because the primary user need is a chronological daily plan.
Priority provides a secondary sort axis when the owner wants to know what matters most right now, independent of clock time.
Due date is used for filtering — `todays_schedule()` only surfaces tasks due today so the view is not cluttered with future or past items.
The decision to weight time over priority by default reflects the reality that many pet care tasks have hard time constraints (medication must be given at the right hour), whereas priority is more useful for quick triage when time is tight.

**b. Tradeoffs**

The conflict detector only flags tasks that share an *exact* time string (e.g., both at "07:30").
It does not detect *overlapping duration windows* — two tasks at 07:00 (60 min) and 07:45 (30 min) would not be flagged even though they overlap.
This tradeoff is reasonable for a pet-care app because most tasks are short and pet owners typically think in terms of named time slots ("morning", "noon") rather than precise durations.
A full interval-overlap check would require converting each task to a `(start_minutes, end_minutes)` range, sorting, and sweeping — correct but significantly more complex for the edge-case benefit it provides.

---

## 3. AI Collaboration

**a. How you used AI**

AI was used in three distinct ways during this project.
First, for *design brainstorming* — generating the initial Mermaid.js UML sketch and discussing where conflict detection logically belongs (Pet vs. Scheduler).
Second, for *scaffolding* — producing the dataclass skeletons and method stubs from the UML so the file structure was consistent from the start.
Third, for *test generation* — drafting the pytest suite structure, including fixture ideas (`owner_with_two_pets`, `simple_pet`) and edge-case suggestions like the three-way conflict test.
The most effective prompts were specific and contextual: "given this `Scheduler.detect_conflicts()` method, what edge cases should the test suite cover?" yielded more actionable output than broad prompts like "help me test my app."

**b. Judgment and verification**

One AI suggestion that was modified was for the recurrence logic.
The initial AI-generated version of `mark_complete()` mutated the existing task's `due_date` field and reset `completed` to `False` — effectively recycling the same object.
This was rejected because it destroys the completion history: the owner can no longer see that a task was done on a specific date.
The final design returns a *new* `Task` object for the next occurrence while leaving the original immutably completed, which preserves an auditable record.
Verification was done by writing `test_recurrence_preserves_attributes` and `test_mark_complete_appends_next_task_to_pet` to confirm the old task stays completed and a distinct new task appears.

---

## 4. Testing and Verification

**a. What you tested**

The 23 tests cover: task completion flag changes, recurrence object creation (daily and weekly), one-off task returning None, adding/removing tasks from a pet, owner aggregation across multiple pets, chronological sort correctness, priority sort ordering, pet-name filtering, completion-status filtering, due-date filtering, exact-time conflict detection, three-way conflict grouping, and the `Scheduler.mark_task_complete()` integration path.
These tests are important because the algorithmic correctness of sorting and conflict detection is non-obvious — a subtle bug (e.g., lexicographic sort failing on "9:00" vs "10:00") would not be visible from the UI but would silently produce wrong schedules.

**b. Confidence**

Confidence level: ★★★★☆.
All 23 tests pass and cover the main happy paths and primary edge cases.
The most significant gap is the lack of tests for invalid or malformed input (e.g., a time string of "25:99"), since the current implementation trusts the UI to validate before creating a `Task`.
The next tests to add would be: overlapping-duration conflict detection (if that feature is added), serialization round-trips for JSON persistence, and multi-day schedule generation.

---

## 5. Reflection

**a. What went well**

The "CLI-first" workflow — building and verifying `pawpal_system.py` through `main.py` before touching `app.py` — was the most effective structural decision.
It meant that every Streamlit button click was wiring to code that had already been shown to work, eliminating an entire class of debugging sessions that mix UI state bugs with logic bugs.

**b. What you would improve**

Given another iteration, the `Task.time` field would be changed from a plain string to a `datetime.time` object.
Using strings was convenient for quick sorting (HH:MM lexicographic order works correctly for 24-hour times) but it creates a silent failure mode: "9:00" would sort *after* "10:00" because "9" > "1" lexicographically.
The current code sidesteps this by enforcing zero-padded input in the UI, but a `datetime.time` attribute would make the invariant explicit and testable.

**c. Key takeaway**

The most important lesson from this project is that AI is most valuable when you treat it as a *fast first drafter* rather than a *final decision maker*.
Every time the AI produced a suggestion — a class design, a test case, an algorithm — the critical step was evaluating whether the suggestion fit the system's invariants and the user's actual needs, not just whether it looked correct in isolation.
The mutation-vs-immutability decision in `mark_complete()` is the clearest example: the AI's version worked but destroyed information.
Being the "lead architect" means holding the design intent in your head and using that as the filter for all AI output.
